from minio import Minio
from pymongo import MongoClient

MONGO_CLIENT = MongoClient("mongodb://root:rootpassword@localhost:9510")
SIMPLEFLOW_DATABASE = MONGO_CLIENT["simpleflow"]
CELERY_COLLECTION = MONGO_CLIENT["celery"]["celery_taskmeta"]

MINIO_CLIENT = Minio(
    endpoint="localhost:9520",
    access_key="root",
    secret_key="rootpassword",
    secure=False,
)

