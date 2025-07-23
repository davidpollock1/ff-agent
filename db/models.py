from __future__ import annotations
from sqlmodel import SQLModel, Field
from clients.DTOs.odds_api_dtos import NFLEventDTO, OutcomeDTO


class NFLEvent(SQLModel, table=True):
    id: str = Field(primary_key=True)
    sport_key: str
    sport_title: str
    commence_time: str = Field(...)
    home_team: str = Field(...)
    away_team: str = Field(...)

    @classmethod
    def from_dto(cls, dto: NFLEventDTO) -> NFLEvent:
        return cls(**dto.model_dump())


class Outcome(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(...)
    price: int = Field(...)
    point: float = Field(...)

    bookmaker: str
    market: str = Field(...)
    event_id: str = Field(foreign_key="nflevent.id")

    @classmethod
    def from_dto(cls, dto: OutcomeDTO) -> Outcome:
        return cls(**dto.model_dump())
