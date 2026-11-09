from fastapi import FastAPI

from database import Base, engine
import models
from api import router as flight_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelTech Flight Service")

app.include_router(flight_router)


@app.get("/")
def root():
    return {"message": "Flight Service is running"}