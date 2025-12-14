from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from app.core.settings import settings

engine = create_engine(
    settings.database_url,
    echo=settings.environment == "local",
    pool_pre_ping=True,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
