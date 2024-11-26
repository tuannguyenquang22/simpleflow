from fastapi import APIRouter

from app.learner.schema import LearnerCreate, LearnerUpdate
from app.learner import service


router = APIRouter(prefix="/api/v1/learner", tags=["learner"])


@router.post("/")
def create_learner(item: LearnerCreate):
    try:
        data = service.create_learner(item)
        response = data.model_dump()
        return {"status": 100, "message": "Learner created successfully", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.get("/run/{id}")
def training(id: str):
    try:
        data = service.training(id)
        return {"status": 100, "message": "Training completed", "data": data}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.get("/{id}")
def get_learner_by_id(id: str):
    try:
        data, tasks = service.get_learner_by_id(id)
        response = data.model_dump()
        return {"status": 100, "message": "Learner fetched successfully", "data": { "learner": response, "tasks": tasks } }
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.get("/")
def get_all_learners():
    try:
        data = service.get_all_learners()
        if data:
            response = [item.model_dump() for item in data]
        else:
            response = []
        return {"status": 100, "message": "Learners fetched successfully", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.put("/{id}")
def update_learner_by_id(id: str, item: LearnerUpdate):
    try:
        data = service.update_learner_by_id(id, item)
        response = data.model_dump()
        return {"status": 100, "message": "Learner updated successfully", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.delete("/{id}")
def delete_learner_by_id(id: str):
    try:
        data = service.delete_learner_by_id(id)
        response = data.model_dump()
        return {"status": 100, "message": "Learner deleted successfully", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.get("/task/{task_id}")
def get_task(task_id: str):
    try:
        data = service.get_task_by_id(task_id)
        return {"status": 100, "message": "Task fetched successfully", "data": data}
    except Exception as e:
        return {"status": 200, "message": str(e)}