from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.database import Base, engine
from app.models import user, inspection
from app.routers import auth, inspections, users


app = FastAPI(
    title="Inspection Management API",
    version="1.0.0",
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(inspections.router)
app.include_router(users.router)