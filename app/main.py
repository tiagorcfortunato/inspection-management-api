from fastapi import FastAPI

from app.database import Base, engine
from app.models import user, inspection
from app.routers import auth, inspections, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inspection Management API",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(inspections.router)
app.include_router(users.router)