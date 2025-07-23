from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from clients.DTOs.odds_api_dtos import EventOddsResponseDTO


class Outcome(BaseModel):
    name: str
    description: str
    price: int
    point: Optional[float] = None


class Market(BaseModel):
    event_id: Optional[str] = None
    player_id: Optional[str] = None
    key: Optional[str] = None
    last_update: Optional[str] = None
    outcomes: List[Outcome] = []

    @classmethod
    def from_event_odds_response_dto(cls, dto: EventOddsResponseDTO) -> List[Market]:
        markets = []
        for bookmaker in dto.bookmakers:
            for market_dto in bookmaker.markets:
                outcomes = [
                    Outcome(
                        name=outcome.name,
                        description=outcome.description,
                        price=outcome.price,
                        point=outcome.point,
                    )
                    for outcome in market_dto.outcomes
                ]
                market = cls(
                    event_id=dto.id,
                    key=market_dto.key,
                    last_update=market_dto.last_update,
                    outcomes=outcomes,
                )
                markets.append(market)
        return markets
