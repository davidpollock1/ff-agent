from fastapi import APIRouter, Depends
from sqlmodel import Session, text
from app.core.db import get_session

router = APIRouter()


@router.get("/health/db")
def db_health(session: Session = Depends(get_session)) -> dict[str, str]:
    session.exec(text("SELECT 1"))
    return {"status": "ok"}
