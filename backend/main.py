from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.datasource.router import router as datasource_router
from app.featureset.router import router as featureset_router
from app.learner.router import router as learner_router
import uvicorn


app = FastAPI()
app.include_router(datasource_router)
app.include_router(featureset_router)
app.include_router(learner_router)


origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080, log_level="info",)