from fastapi import FastAPI

from database import Base, engine
import models
from api import router as monitoring_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelTech Flight Monitoring Service")
app.include_router(monitoring_router)


@app.get("/")
def root():
    return {"message": "Flight Monitoring Service is running"}