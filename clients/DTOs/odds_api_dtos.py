from pydantic import BaseModel
from typing import List


class NFLEventDTO(BaseModel):
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str


class NFLEventResponseDTO(BaseModel):
    events: List[NFLEventDTO]


class OutcomeDTO(BaseModel):
    name: str
    price: int
    point: float


class MarketDTO(BaseModel):
    key: str
    last_update: str
    outcomes: List[OutcomeDTO]


class BookmakerDTO(BaseModel):
    key: str
    title: str
    markets: List[MarketDTO]


class EventOddsResponseDTO(BaseModel):
    id: str = ""
    sport_key: str = ""
    sport_title: str = ""
    commence_time: str = ""
    home_team: str = ""
    away_team: str = ""
    bookmakers: List[BookmakerDTO] = []
