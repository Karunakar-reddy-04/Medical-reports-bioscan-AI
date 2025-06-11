from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database, routes

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
