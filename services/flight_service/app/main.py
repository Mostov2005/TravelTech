
from threading import Thread

from fastapi import FastAPI

from database import Base, engine
import models
from api import router as flight_router
from grpc_server import serve


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelTech Flight Service")

app.include_router(flight_router)


@app.on_event("startup")
def start_grpc_server():
    Thread(
        target=serve,
        daemon=True
    ).start()


@app.get("/")
def root():
    return {"message": "Flight Service is running"}
