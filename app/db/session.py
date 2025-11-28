from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from app.models import *
from .config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.ECHO_SQL, future=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
