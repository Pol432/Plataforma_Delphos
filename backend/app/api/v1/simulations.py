from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.simulation import SimulationCreate, SimulationOut, SimulationUpdate
from app.services.simulation_service import SimulationService
from app.schemas.progress import SubmissionPayload, SubmissionResultOut, FinishSimulationPayload
from app.api.deps import get_current_user
from app.models.user import User

# FIX: Router responde a ambas rutas
router = APIRouter()

@router.post("", response_model=SimulationOut, status_code=status.HTTP_201_CREATED)
def create_simulation(sim_data: SimulationCreate, db: Session = Depends(get_db)):
    service = SimulationService(db)
    return service.create_simulation(sim_data.model_dump())

@router.get("", response_model=List[SimulationOut])
def list_simulations(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    state: Optional[str] = Query(
        "published",
        description="Estado a filtrar. Por defecto solo 'published'; usar 'all' para incluir draft/archived.",
    ),
    db: Session = Depends(get_db),
):
    service = SimulationService(db)
    # `state=all` es la vía explícita (ej. admin) para ver también draft/archived.
    state_filter = None if state == "all" else state
    return service.list_simulations(skip, limit, company_id, state_filter)

@router.get("/{sim_id}", response_model=SimulationOut)
def get_simulation(sim_id: int, db: Session = Depends(get_db)):
    service = SimulationService(db)
    sim = service.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    return sim

@router.put("/{sim_id}", response_model=SimulationOut)
def update_simulation(sim_id: int, sim_data: SimulationUpdate, db: Session = Depends(get_db)):
    service = SimulationService(db)
    return service.update_simulation(sim_id, sim_data.model_dump(exclude_unset=True))

@router.delete("/{sim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_simulation(sim_id: int, db: Session = Depends(get_db)):
    service = SimulationService(db)
    service.delete_simulation(sim_id)
    return None

@router.post("/{sim_id}/inscribir")
def enroll_user(
    sim_id: int,
    user_id: int = Query(1, description="ID del usuario (opcional si hay token)"),
    db: Session = Depends(get_db)
):
    service = SimulationService(db)
    return service.enroll_user(sim_id, user_id)


@router.post("/{simulation_id}/tasks/{task_id}/submit", response_model=SubmissionResultOut)
def submit_task(
    simulation_id: int,
    task_id: int,
    payload: SubmissionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SimulationService(db)
    result = service.submit_task_answer(
        user_id=current_user.id,
        simulation_id=simulation_id,
        task_id=task_id,
        answer_text=payload.respuesta_texto or payload.response or payload.user_answer,
    )
    return SubmissionResultOut(**result)


@router.post("/{simulation_id}/finish")
def finish_simulation(
    simulation_id: int,
    payload: Optional[FinishSimulationPayload] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SimulationService(db)
    payload_data = payload.model_dump(exclude_unset=True) if payload else {}
    return service.finish_simulation(
        user_id=current_user.id,
        simulation_id=simulation_id,
        current_user=current_user,
        payload=payload_data,
    )
