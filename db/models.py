from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from clients.DTOs.odds_api_dtos import EventOddsResponseDTO


class BettingOdds(BaseModel):
    event_id: Optional[str] = Field(
        default=None, description="Unique identifier for the event"
    )
    player_id: Optional[str] = Field(
        default=None, description="Player identifier if applicable"
    )
    player_name: Optional[str] = Field(
        ...,
        description="Name of the player if applicable.",
    )
    key: Optional[str] = Field(default=None, description="Odds type.")
    type: str = Field(..., description="Name of the outcome. Over, Under, etc...")
    price: int = Field(..., description="Odds price for the outcome")
    point: Optional[float] = Field(
        default=None, description="Point value for the outcome if applicable"
    )

    @classmethod
    def from_event_odds_response_dto(
        cls, dto: EventOddsResponseDTO, player_map: dict = {}
    ) -> List[BettingOdds]:
        betting_odds = []
        for bookmaker in dto.bookmakers:
            for market_dto in bookmaker.markets:
                for outcome in market_dto.outcomes:
                    player_id = None
                    player_name = None
                    if outcome.description:
                        player_name = outcome.description
                        player_id = player_map.get(player_name, "")

                    odds = cls(
                        event_id=dto.id,
                        player_id=str(player_id),
                        player_name=player_name,
                        key=market_dto.key,
                        type=outcome.name,
                        price=outcome.price,
                        point=outcome.point,
                    )
                    betting_odds.append(odds)
        return betting_odds
