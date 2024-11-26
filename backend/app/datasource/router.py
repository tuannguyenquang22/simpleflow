from fastapi import APIRouter

from app.datasource.schema import DataSourceCreate
from app.datasource import service


router = APIRouter(prefix="/api/v1/datasource", tags=["datasource"])


@router.post("/")
def create(item: DataSourceCreate):
    try:
        data = service.create_datasource(item)
        response = data.model_dump()
        return {"status": 100, "message": "Data source created successfully", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.get("/")
def get_all():
    try:
        data = service.get_all_datasources()
        if data:
            response = [item.model_dump() for item in data]
        else:
            response = []
        return {"status": 100, "message": "Data sources fetched successfully", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.get("/{id}")
def get_by_name(id: str):
    try:
        data = service.get_datasource_by_id(id)
        response = data.model_dump()
        return {"status": 100, "message": "Data source fetched successfully", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}