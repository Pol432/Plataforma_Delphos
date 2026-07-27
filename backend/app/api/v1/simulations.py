from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.simulation import SimulationCreate, SimulationOut
from app.services.simulation_service import SimulationService
from app.schemas.simulations import SimulationCreate, SimulationUpdate, SimulationOut

# FIX: Router responde a ambas rutas
router = APIRouter()

@router.post("", response_model=SimulationOut, status_code=status.HTTP_201_CREATED)
def create_simulation(sim_data: SimulationCreate, db: Session = Depends(get_db)):
    service = SimulationService(db)
    return service.create_simulation(sim_data.model_dump())

@router.get("", response_model=List[SimulationOut])
def list_simulations(skip: int = 0, limit: int = 100, company_id: Optional[int] = None, state: Optional[str] = None, db: Session = Depends(get_db)):
    service = SimulationService(db)
    return service.list_simulations(skip, limit, company_id, state)

@router.get("/{sim_id}", response_model=SimulationOut)
def get_simulation(sim_id: int, db: Session = Depends(get_db)):
    service = SimulationService(db)
    sim = service.get_simulation(sim_id)
    if not sim: raise HTTPException(status_code=404, detail="Simulación no encontrada")
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
