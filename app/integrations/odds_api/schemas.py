from pydantic import BaseModel
from typing import List, Optional


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
    description: str = ""
    price: int
    point: Optional[float] = None


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
