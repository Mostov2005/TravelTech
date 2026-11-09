from fastapi import FastAPI

from database import Base, engine
import models
from api import router as recovery_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelTech Recovery Service")

app.include_router(recovery_router)


@app.get("/")
def root():
    return {"message": "Recovery Service is running"}