from fastapi import FastAPI

from database import Base, engine
import models
from api import router as identity_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelTech Identity Service")

app.include_router(identity_router)


@app.get("/")
def root():
    return {"message": "Identity Service is running"}