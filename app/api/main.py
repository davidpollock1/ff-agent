from fastapi import APIRouter, FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
from clients.sports_odds_api_client import SportsOddsApiClient


app = FastAPI()

router = APIRouter()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/home")
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/intake/")
async def intake(
    deps: Annotated[dict, Depends(SportsOddsApiClient)],
) -> HTMLResponse:
    return templates.TemplateResponse("home.html", {"request": commons})


app.include_router(router)
