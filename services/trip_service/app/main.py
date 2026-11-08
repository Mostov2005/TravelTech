from fastapi import FastAPI

from database import Base, engine
import models
from api import router as trip_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelTech Trip Service")

app.include_router(trip_router)


@app.get("/")
def root():
    return {"message": "Trip Service is running"}