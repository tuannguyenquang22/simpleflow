from bson import ObjectId
from app.database import SIMPLEFLOW_DATABASE, CELERY_COLLECTION
from app.learner.model import Learner
from app.learner.schema import LearnerCreate
from worker.tasks import execute_training
import app.featureset.service as featureset_service


def create_learner(
    item: LearnerCreate
):
    try:
        learner = Learner(**item.model_dump())
        data = SIMPLEFLOW_DATABASE["learner"].insert_one(item.model_dump())
        learner.id = str(data.inserted_id)
    except Exception:
        raise Exception("Failed to save learner")

    return learner

def training(
    id: str,
):
    try:
        data =  SIMPLEFLOW_DATABASE["learner"].find_one({"_id": ObjectId(id)})
        data["_id"] = str(data["_id"])
        learner = Learner(**data)
    except Exception:
        raise Exception("Failed to get learner")

    featureset = featureset_service.get_featureset_by_id(learner.feature_set_id)

    bucket_name = "simpleflow"
    object_name = f"featureset/{featureset.id}"
    target_column = featureset.target.column

    celery_task = execute_training.delay(
        learner_id=learner.id,
        bucket_name=bucket_name,
        object_name=object_name,
        target_column=target_column,
        problem_type=learner.problem_type,
        algorithm=learner.algorithm,
        test_size=learner.test_size,
        tuning=learner.tuning,
    )

    return {"task_id": str(celery_task.id)}


def get_all_learners():
    try:
        learners = []
        for learner in SIMPLEFLOW_DATABASE["learner"].find():
            learner["_id"] = str(learner["_id"])
            learners.append(Learner(**learner))
        return learners
    except Exception:
        raise Exception("Failed to get learners")


def get_learner_by_id(id: str):
    try:
        data = SIMPLEFLOW_DATABASE["learner"].find_one({"_id": ObjectId(id)})
        data["_id"] = str(data["_id"])

        tasks = []
        training_tasks = CELERY_COLLECTION.find({"learner_id": id})
        for task in training_tasks:
            task["_id"] = str(task["_id"])
            tasks.append(task)

        return Learner(**data), tasks
    except Exception:
        raise Exception("Failed to get learner")


def update_learner_by_id(id: str, item: LearnerCreate):
    try:
        data = SIMPLEFLOW_DATABASE["learner"].find_one({"_id": ObjectId(id)})
        if data:
            data.update(item.model_dump())
            SIMPLEFLOW_DATABASE["learner"].update_one({"_id": ObjectId(id)}, {"$set": data})
            return Learner(**data)
        else:
            raise Exception("Learner not found")
    except Exception:
        raise Exception("Failed to update learner")


def delete_learner_by_id(id: str):
    try:
        data = SIMPLEFLOW_DATABASE["learner"].find_one({"_id": ObjectId(id)})
        if data:
            SIMPLEFLOW_DATABASE["learner"].delete_one({"_id": ObjectId(id)})
            return Learner(**data)
        else:
            raise Exception("Learner not found")
    except Exception:
        raise Exception("Failed to delete learner")


def get_task_by_id(task_id: str):
    try:
        task = CELERY_COLLECTION.find_one({"_id": ObjectId(task_id)})
        task["_id"] = str(task["_id"])
        return task
    except Exception:
        raise Exception("Failed to get task")