from fastapi import FastAPI

from database import Base, engine
import models
from api import router as trip_router

from threading import Thread

from messaging import run_outbox_worker

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelTech Trip Service")

Thread(
    target=run_outbox_worker,
    daemon=True
).start()

app.include_router(trip_router)


@app.get("/")
def root():
    return {"message": "Trip Service is running"}
