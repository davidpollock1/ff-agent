from sqlmodel import SQLModel, Session, create_engine, select
from contextlib import contextmanager
from typing import List, TypeVar
from .models import NFLEvent


DATABASE_URL = "sqlite:///./ffagent.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session


def upsert_object(nfl_event: NFLEvent, id: str) -> NFLEvent:
    with get_session() as session:
        statement = select(NFLEvent).where(NFLEvent.id == id)  # type: ignore
        result = session.exec(statement).first()

        if result is None:
            result = nfl_event

        for key, value in nfl_event.dict(exclude_unset=True).items():
            setattr(result, key, value)

        session.add(result)
        session.commit()
        session.refresh(result)

        return result
