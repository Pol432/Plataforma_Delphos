"""
Content API - Complete CRUD for Modules, Tasks, Resources
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.db.session import get_db
from app.models.simulations import SimulationModule, ModuleTask, TaskResource
from app.schemas.simulation import (
    ModuleCreate, ModuleUpdate, ModuleOut,
    TaskCreate, TaskUpdate, TaskOut,
    ResourceCreate, ResourceUpdate, ResourceOut
)

router = APIRouter()


# =============================================================================
# MODULES ENDPOINTS
# =============================================================================

@router.post("/modules", response_model=ModuleOut, status_code=status.HTTP_201_CREATED)
def create_module(module: ModuleCreate, db: Session = Depends(get_db)):
    """Create new module"""
    try:
        db_module = SimulationModule(**module.model_dump())
        db.add(db_module)
        db.commit()
        db.refresh(db_module)
        return db_module
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module creation failed - check simulation_id exists"
        )


@router.get("/modules", response_model=List[ModuleOut])
def list_modules(
    simulation_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List modules, optionally filtered by simulation"""
    query = db.query(SimulationModule)
    
    if simulation_id:
        query = query.filter(SimulationModule.simulation_id == simulation_id)
    
    return query.offset(skip).limit(limit).all()


@router.get("/modules/{module_id}", response_model=ModuleOut)
def get_module(module_id: int, db: Session = Depends(get_db)):
    """Get specific module"""
    module = db.query(SimulationModule).filter(SimulationModule.id == module_id).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    return module


@router.patch("/modules/{module_id}", response_model=ModuleOut)
def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    db: Session = Depends(get_db)
):
    """Update module"""
    module = db.query(SimulationModule).filter(SimulationModule.id == module_id).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    update_dict = module_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(module, field, value)
    
    db.commit()
    db.refresh(module)
    return module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(module_id: int, db: Session = Depends(get_db)):
    """Delete module"""
    module = db.query(SimulationModule).filter(SimulationModule.id == module_id).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    db.delete(module)
    db.commit()
    return None


# =============================================================================
# TASKS ENDPOINTS
# =============================================================================

@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create new task (Fix: Maps 'type' -> 'task_type')"""
    try:
        # MAPEO MANUAL: Pydantic 'type' -> SQLAlchemy 'task_type'
        task_data = task.model_dump()
        if 'type' in task_data:
            task_data['task_type'] = task_data.pop('type')
            
        VALID_TASK_FIELDS = {'module_id','title','description','order','task_type','instructor_name','instructor_role','instructor_video_url','estimated_minutes','xp_reward'}
        task_data = {k:v for k,v in task_data.items() if k in VALID_TASK_FIELDS}
        db_task = ModuleTask(**task_data)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # Re-map for response if needed, but Pydantic handles alias usually
        # For simplicity, we return the DB object which has task_type
        # The response model expects 'type', so we might need a property on the model
        # or just rely on from_attributes doing the mapping if aliases set up.
        # But here we just return db_task.
        return db_task
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task creation failed - check module_id exists"
        )


@router.get("/tasks", response_model=List[TaskOut])
def list_tasks(
    module_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List tasks, optionally filtered by module"""
    query = db.query(ModuleTask)
    
    if module_id:
        query = query.filter(ModuleTask.module_id == module_id)
    
    tasks = query.offset(skip).limit(limit).all()
    # Manual mapping for response list if aliases fail
    for t in tasks:
        if not hasattr(t, 'type'):
            t.type = t.task_type
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get specific task"""
    task = db.query(ModuleTask).filter(ModuleTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    # Map for response
    if not hasattr(task, 'type'):
        task.type = task.task_type
        
    return task


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update task"""
    task = db.query(ModuleTask).filter(ModuleTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    update_dict = task_data.model_dump(exclude_unset=True)
    
    # MAPEO MANUAL en Update
    if 'type' in update_dict:
        update_dict['task_type'] = update_dict.pop('type')
        
    for field, value in update_dict.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    # Map for response
    if not hasattr(task, 'type'):
        task.type = task.task_type
        
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete task"""
    task = db.query(ModuleTask).filter(ModuleTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    db.delete(task)
    db.commit()
    return None


# =============================================================================
# RESOURCES ENDPOINTS
# =============================================================================

@router.post("/resources", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    """Create new resource"""
    try:
        db_resource = TaskResource(
            name=resource.title,
            **resource.model_dump(exclude={"title"})
        )
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        return db_resource
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource creation failed - check task_id exists"
        )


@router.get("/resources", response_model=List[ResourceOut])
def list_resources(
    task_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List resources, optionally filtered by task"""
    query = db.query(TaskResource)
    
    if task_id:
        query = query.filter(TaskResource.task_id == task_id)
    
    return query.offset(skip).limit(limit).all()


@router.get("/resources/{resource_id}", response_model=ResourceOut)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """Get specific resource"""
    resource = db.query(TaskResource).filter(TaskResource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with id {resource_id} not found"
        )
    
    return resource


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    """Delete resource"""
    resource = db.query(TaskResource).filter(TaskResource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with id {resource_id} not found"
        )
    
    db.delete(resource)
    db.commit()
    return None
