from fastapi import APIRouter, FastAPI
from app.core.db import engine
from sqlmodel import SQLModel
from app.health.routes import router as health_router
from app.auth.routes import router as auth_router
from app.league.routes import router as league_router

app = FastAPI()
router = APIRouter()


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


app.include_router(router)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(league_router)
