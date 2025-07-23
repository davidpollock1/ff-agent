from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from clients.DTOs.odds_api_dtos import EventOddsResponseDTO


class Outcome(BaseModel):
    name: str
    price: int
    point: Optional[float] = None


class Market(BaseModel):
    key: str
    last_update: str
    outcomes: List[Outcome]


class Event(BaseModel):
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str
    markets: List[Market] = []

    @classmethod
    def from_event_odds_response_dto(cls, dto: EventOddsResponseDTO) -> Event:
        markets = (
            [
                Market(
                    key=market.key,
                    last_update=market.last_update,
                    outcomes=[
                        Outcome(
                            name=outcome.name, price=outcome.price, point=outcome.point
                        )
                        for outcome in market.outcomes
                    ],
                )
                for market in dto.bookmakers[0].markets
            ]
            if dto.bookmakers
            else []
        )

        return cls(
            id=dto.id,
            sport_key=dto.sport_key,
            sport_title=dto.sport_title,
            commence_time=dto.commence_time,
            home_team=dto.home_team,
            away_team=dto.away_team,
            markets=markets,
        )
