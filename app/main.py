from fastapi import FastAPI

from app.routers import auth, inspections

app = FastAPI(
    title="Inspection Management API",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(inspections.router)


@app.get("/")
def root():
    return {"message": "Inspection Management API is running"}