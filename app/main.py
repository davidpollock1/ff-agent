from fastapi import APIRouter, FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from app.core.db import get_session, engine
from sqlmodel import SQLModel
from app.health.routes import router as health_router
from app.auth.routes import router as auth_router

app = FastAPI()
router = APIRouter()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


@router.get("/")
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/home")
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/intake/")
async def intake(sessions: Session = Depends(get_session)) -> str:
    return "Intake endpoint"


app.include_router(router)
app.include_router(health_router)
app.include_router(auth_router)