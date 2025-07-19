from pydantic import BaseModel
from typing import List


class NFLEvent(BaseModel):
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str


class NFLEventResponse(BaseModel):
    events: List[NFLEvent]


class Outcome(BaseModel):
    name: str
    price: int
    point: float


class Market(BaseModel):
    key: str
    last_update: str
    outcomes: List[Outcome]


class Bookmaker(BaseModel):
    key: str
    title: str
    markets: List[Market]


class EventOddsResponse(BaseModel):
    id: str = ""
    sport_key: str = ""
    sport_title: str = ""
    commence_time: str = ""
    home_team: str = ""
    away_team: str = ""
    bookmakers: List[Bookmaker] = []
