from pydantic import BaseModel, Field
from typing import List


class LineupEntry(BaseModel):
    player_name: str = Field(..., description="The full name of the player")
    assigned_slot: str = Field(
        ...,
        description="The lineup slot the player should be placed in (e.g. RB, FLEX, WR)",
    )


class LineupChangeSummary(BaseModel):
    benched_players: List[str] = Field(
        ..., description="List of players being benched compared to the previous lineup"
    )
    promoted_players: List[str] = Field(
        ..., description="List of players being promoted to starting lineup"
    )
    reasoning: str = Field(..., description="Short explanation of the changes made")


class LineupRecommendationOutput(BaseModel):
    optimal_lineup: List[LineupEntry] = Field(
        ..., description="The recommended full lineup for this week"
    )
    changes_summary: LineupChangeSummary = Field(
        ..., description="Summary of changes compared to previous week"
    )
