# Yêu cầu

* Python 3.12
* Docker 27.1.1
* Docker Compose v2.29.1

```bash
pip install -r requirements.txt
```

# Cài đặt CSDL

```bash
docker compose up -d
```



# Chạy API Server
```bash
python main.py
```

# Chạy Celery Worker
```bash
celery -A worker.celery_app worker --loglevel=info
```