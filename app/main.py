from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routers import tasks, auth


app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "Database connected"}