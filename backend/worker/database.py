from minio import Minio


MINIO_CLIENT = Minio(
    endpoint="localhost:9520",
    access_key="root",
    secret_key="rootpassword",
    secure=False,
)

