from fastapi import APIRouter
from app.featureset import service
from app.featureset.schema import FeatureSetCreate, FeatureSetProfiling


router = APIRouter(prefix="/api/v1/featureset", tags=["featureset"])


@router.post("/profiling")
def profiling(item: FeatureSetProfiling):
    try:
        data = service.profiling(item)
        return {"status": 100, "message": "Profiling completed", "data": data}
    except Exception as e:
        return {"status": 200, "message": str(e)}
    

@router.post("/")
def create(item: FeatureSetCreate):
    try:
        data = service.create_featureset(item)
        return {"status": 100, "message": "EDA completed", "data": data}
    except Exception as e:
        return {"status": 200, "message": str(e)}
    

@router.get("/")
def get_all_featuresets():
    try:
        data = service.get_all_featuresets()
        if data:
            response = [item.model_dump() for item in data]
        else:
            response = []
        return {"status": 100, "message": "Completed", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.get("/{id}")
def get_featureset_by_id(id: str):
    try:
        data = service.get_featureset_by_id(id)
        response = data.model_dump()
        return {"status": 100, "message": "Completed", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}


@router.delete("/{id}")
def delete_featureset_by_id(id: str):
    try:
        data = service.delete_featureset_by_id(id)
        response = data.model_dump()
        return {"status": 100, "message": "Completed", "data": response}
    except Exception as e:
        return {"status": 200, "message": str(e)}