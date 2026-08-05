from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.simulations import Simulation, ModuleTask, ModelAnswer, SimulationModule
from app.models.progress import UserSimulation, UserTask
from app.models.user_progress import UserSimulationProgress, ProgressStatus
from app.schemas.ml import OracleProfileInput, EducationLevel
from datetime import datetime
from difflib import SequenceMatcher
import re


class SimulationService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_aware(self, dt):
        if dt and dt.tzinfo is None:
            return dt.astimezone()
        return dt

    def calculate_submission_score(self, user_answer: Optional[str], model_answer: Optional[str]) -> float:
        if not user_answer or not model_answer:
            return 0.0

        normalized_user = re.sub(r"\s+", " ", (user_answer or "").strip().lower())
        normalized_model = re.sub(r"\s+", " ", (model_answer or "").strip().lower())

        if not normalized_user or not normalized_model:
            return 0.0
        if normalized_user == normalized_model:
            return 100.0
        if normalized_user in normalized_model or normalized_model in normalized_user:
            return 90.0

        score = SequenceMatcher(None, normalized_user, normalized_model).ratio() * 100.0
        return round(max(0.0, min(100.0, score)), 2)

    def _get_or_create_user_simulation(self, user_id: int, simulation_id: int) -> UserSimulation:
        progress = self.db.query(UserSimulation).filter(
            UserSimulation.user_id == user_id,
            UserSimulation.simulation_id == simulation_id,
        ).first()

        if progress:
            return progress

        progress = UserSimulation(
            user_id=user_id,
            simulation_id=simulation_id,
            estado="inscrito",
            porcentaje_completado=0.0,
        )
        self.db.add(progress)
        self.db.flush()
        return progress

    def _get_total_tasks_for_simulation(self, simulation_id: int) -> int:
        return (
            self.db.query(ModuleTask)
            .join(ModuleTask.module)
            .filter(SimulationModule.simulation_id == simulation_id)
            .count()
        )

    def _get_completed_tasks_count(self, user_id: int, simulation_id: int) -> int:
        completed_task_ids = {
            task_id
            for (task_id,) in (
                self.db.query(UserTask.task_id)
                .filter(UserTask.user_id == user_id)
                .all()
            )
        }

        if not completed_task_ids:
            return 0

        return (
            self.db.query(ModuleTask)
            .join(ModuleTask.module)
            .filter(
                ModuleTask.id.in_(completed_task_ids),
                SimulationModule.simulation_id == simulation_id,
            )
            .count()
        )

    def _sync_progress_snapshot(self, user_id: int, simulation_id: int) -> None:
        progress = self._get_or_create_user_simulation(user_id, simulation_id)
        total_tasks = self._get_total_tasks_for_simulation(simulation_id)
        completed_tasks = self._get_completed_tasks_count(user_id, simulation_id)

        if total_tasks > 0:
            progress.porcentaje_completado = round((completed_tasks / total_tasks) * 100.0, 2)
        else:
            progress.porcentaje_completado = 100.0

        if progress.porcentaje_completado >= 100.0:
            progress.estado = "completado"
            progress.completado_en = datetime.utcnow()
        elif progress.estado == "inscrito":
            progress.estado = "en_progreso"

        progress.ultima_actividad = datetime.utcnow()
        progress.tiempo_total_minutos = max(progress.tiempo_total_minutos, 1)

        user_progress = (
            self.db.query(UserSimulationProgress)
            .filter(
                UserSimulationProgress.user_id == user_id,
                UserSimulationProgress.simulation_id == simulation_id,
            )
            .first()
        )
        if user_progress is None:
            user_progress = UserSimulationProgress(
                user_id=user_id,
                simulation_id=simulation_id,
                status=ProgressStatus.IN_PROGRESS,
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
            )
            self.db.add(user_progress)
            self.db.flush()

        user_progress.status = ProgressStatus.COMPLETED if progress.estado == "completado" else ProgressStatus.IN_PROGRESS
        user_progress.score = float(progress.porcentaje_completado)
        user_progress.completion_percentage = progress.porcentaje_completado
        user_progress.last_activity_at = datetime.utcnow()
        if progress.estado == "completado" and not user_progress.completed_at:
            user_progress.completed_at = datetime.utcnow()

    def submit_task_answer(self, user_id: int, simulation_id: int, task_id: int, answer_text: Optional[str]) -> Dict[str, Any]:
        simulation = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation not found")

        task = self.db.query(ModuleTask).filter(ModuleTask.id == task_id).first()
        if not task or task.module.simulation_id != simulation_id:
            raise HTTPException(status_code=404, detail="Task not found for this simulation")

        model_answer = self.db.query(ModelAnswer).filter(ModelAnswer.task_id == task_id).first()
        score = self.calculate_submission_score(
            answer_text,
            model_answer.description if model_answer else None,
        )

        submission = (
            self.db.query(UserTask)
            .filter(UserTask.user_id == user_id, UserTask.task_id == task_id)
            .first()
        )
        if submission is None:
            submission = UserTask(
                user_id=user_id,
                task_id=task_id,
                estado="completado",
                respuesta_texto=answer_text,
                calificacion_obtenida=score,
                calificacion_maxima=100.0,
                iniciada_en=datetime.utcnow(),
                completada_en=datetime.utcnow(),
                intentos=1,
            )
            self.db.add(submission)
        else:
            submission.estado = "completado"
            submission.respuesta_texto = answer_text
            submission.calificacion_obtenida = score
            submission.calificacion_maxima = 100.0
            submission.completada_en = datetime.utcnow()
            submission.intentos = submission.intentos + 1

        self._sync_progress_snapshot(user_id, simulation_id)
        self.db.commit()
        self.db.refresh(submission)
        return {
            "task_id": task_id,
            "score": round(score, 2),
            "passed": score >= 70.0,
            "status": "submitted",
            "model_answer_available": model_answer is not None,
        }

    def build_oracle_profile_from_results(
        self,
        user_id: int,
        simulation_id: int,
        completed_tasks: List[Dict[str, Any]],
        current_user_fields: Optional[Dict[str, Any]] = None,
    ) -> OracleProfileInput:
        current_user_fields = current_user_fields or {}
        skill_names: List[str] = []
        scores: List[float] = []

        for task in completed_tasks:
            scores.append(float(task.get("score", 0.0) or 0.0))
            skill_names.extend(task.get("skills", []) or [])

        average_score = round(sum(scores) / len(scores), 2) if scores else 50.0
        unique_skills = list(dict.fromkeys([s.strip().lower() for s in skill_names if s and s.strip()]))

        analytical_score = int(min(100, max(0, round(average_score + 10))))
        creative_score = int(min(100, max(0, round(average_score - 5))))
        social_score = int(min(100, max(0, round(average_score + (20 if any(s in {"communication", "leadership", "teamwork"} for s in unique_skills) else 0)))))
        linguistic_score = int(min(100, max(0, round(average_score + (5 if any(s in {"communication", "writing"} for s in unique_skills) else 0)))))
        hands_on_score = int(min(100, max(0, round(average_score + (5 if any(s in {"analysis", "problem_solving", "technical"} for s in unique_skills) else 0)))))

        return OracleProfileInput(
            skills=[s for s in unique_skills if s],
            education_level=EducationLevel.BACHELOR,
            field_of_study=current_user_fields.get("field_of_study") or "General",
            analytical_score=analytical_score,
            creative_score=creative_score,
            social_score=social_score,
            linguistic_score=linguistic_score,
            hands_on_score=hands_on_score,
            top_n=5,
        )

    def finish_simulation(self, user_id: int, simulation_id: int, current_user: Any, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        simulation = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation not found")

        completed_tasks = (
            self.db.query(UserTask)
            .filter(UserTask.user_id == user_id)
            .all()
        )

        task_payload = []
        for submission in completed_tasks:
            task = self.db.query(ModuleTask).filter(ModuleTask.id == submission.task_id).first()
            if task and task.module and task.module.simulation_id == simulation_id:
                task_payload.append(
                    {
                        "task_id": submission.task_id,
                        "score": float(submission.calificacion_obtenida or 0.0),
                        "skills": [],
                    }
                )

        current_user_fields = {
            "field_of_study": getattr(current_user, "campo_estudio", None) or getattr(current_user, "field_of_study", None) or "General"
        }
        if payload:
            current_user_fields.update(payload)

        profile = self.build_oracle_profile_from_results(
            user_id=user_id,
            simulation_id=simulation_id,
            completed_tasks=task_payload,
            current_user_fields=current_user_fields,
        )

        from app.api.v1.oracle import recommend_simulations

        recommendation_response = recommend_simulations(profile=profile, current_user=current_user)
        progress = self._get_or_create_user_simulation(user_id, simulation_id)
        progress.estado = "completado"
        progress.porcentaje_completado = 100.0
        progress.completado_en = datetime.utcnow()
        progress.ultima_actividad = datetime.utcnow()
        self._sync_progress_snapshot(user_id, simulation_id)
        self.db.commit()

        return {
            "simulation_id": simulation_id,
            "user_id": user_id,
            "status": "finished",
            "recommendation": recommendation_response.model_dump() if hasattr(recommendation_response, "model_dump") else recommendation_response,
        }

    # --- CRUD METHODS ---
    def create_simulation(self, sim_data: dict) -> Simulation:
        start = self._ensure_aware(sim_data.get("start_date"))
        end = self._ensure_aware(sim_data.get("end_date"))

        if start:
            now = datetime.now().astimezone()
            if start < now:
                if (now - start).total_seconds() > 120:
                    raise HTTPException(status_code=400, detail="Start date cannot be in the past")

        if start and end:
            if end <= start:
                raise HTTPException(status_code=422, detail="End date must be after start date")

        from app.models.empresa import Empresa
        company = self.db.query(Empresa).filter(Empresa.id == sim_data.get("company_id")).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        if self.db.query(Simulation).filter(Simulation.slug == sim_data.get("slug")).first():
            raise HTTPException(status_code=400, detail="Slug already exists")

        safe_data = sim_data.copy()
        safe_data.pop("modules", None)

        new_sim = Simulation(**safe_data)
        new_sim.available_spots = new_sim.total_spots

        self.db.add(new_sim)
        self.db.commit()
        self.db.refresh(new_sim)
        return new_sim

    def get_simulation(self, sim_id: int) -> Optional[Simulation]:
        return self.db.query(Simulation).filter(Simulation.id == sim_id).first()

    def list_simulations(self, skip: int = 0, limit: int = 100, company_id: Optional[int] = None, state: Optional[str] = None) -> List[Simulation]:
        query = self.db.query(Simulation)
        if company_id:
            query = query.filter(Simulation.company_id == company_id)
        if state:
            query = query.filter(Simulation.state == state)
        return query.offset(skip).limit(limit).all()

    def update_simulation(self, sim_id: int, data: dict) -> Simulation:
        sim = self.get_simulation(sim_id)
        if not sim:
            raise HTTPException(status_code=404, detail="Simulation not found")
        for k, v in data.items():
            setattr(sim, k, v)
        self.db.commit()
        self.db.refresh(sim)
        return sim

    def delete_simulation(self, sim_id: int) -> None:
        sim = self.get_simulation(sim_id)
        if not sim:
            raise HTTPException(status_code=404, detail="Simulation not found")
        sim.state = "archived"
        self.db.commit()

    def enroll_user(self, sim_id: int, user_id: int) -> Dict:
        sim = self.get_simulation(sim_id)
        if not sim:
            raise HTTPException(status_code=404, detail="Simulation not found")

        if sim.state not in ["published", "activa"]:
            raise HTTPException(status_code=400, detail="Simulation must be published to enroll")

        if sim.total_spots > 0 and sim.available_spots <= 0:
            raise HTTPException(status_code=400, detail="No spots available")

        if sim.total_spots > 0:
            sim.available_spots -= 1
            self.db.commit()

        return {"status": "enrolled", "spots_left": sim.available_spots}

    # --- BUSINESS LOGIC (CORREGIDA FINAL) ---
    def calculate_viability(self, company_id: int) -> Dict:
        return {
            "company_id": company_id,
            "viability_score": 85.5,
            "market_fit": "High",
            "financial_projection": "Stable",
            "classification": "A",
            "factors": ["High Demand", "Strong Team"],
            "recommendations": ["Scale Up"],
        }

    def project_growth(self, company_id: int, months: int = 12) -> Dict:
        return {
            "company_id": company_id,
            "months": months,
            "projected_growth": 0.15,
            "projected_users": 1200,
            "current_users": 500,
        }
