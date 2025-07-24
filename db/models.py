from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from clients.DTOs.odds_api_dtos import EventOddsResponseDTO


class Outcome(BaseModel):
    name: str = Field(..., description="Name of the outcome")
    description: str = Field(
        ...,
        description="Description of the outcome, contains players name for player props.",
    )
    price: int = Field(..., description="Odds price for the outcome")
    player_id: Optional[str] = Field(
        default=None, description="Player identifier if applicable"
    )
    point: Optional[float] = Field(
        default=None, description="Point value for the outcome if applicable"
    )


class Market(BaseModel):
    event_id: Optional[str] = Field(
        default=None, description="Unique identifier for the event"
    )
    key: Optional[str] = Field(default=None, description="Market key or type")
    last_update: Optional[str] = Field(
        default=None, description="Timestamp of the last market update"
    )
    outcomes: List[Outcome] = Field(
        default_factory=list, description="List of possible outcomes for the market"
    )

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
                        player_id="",
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
