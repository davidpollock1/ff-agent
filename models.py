from datetime import datetime
from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import List, Optional


@dataclass
class PositionSlot:
    """A slot on a fantasy football roster."""

    name: str = Field(..., description="Abbreviated name of the position slot.")
    max_allowed: int = Field(
        ..., description="Maximum number of players allowed in this slot."
    )
    # eligible_positions: List[str] = Field(
    #     ..., description="List of positions eligible for this position slot."
    # )
    is_starting_slot: bool = Field(
        ..., description="True if this is a scoring position."
    )


@dataclass
class ScoringRules:
    """The scoring rules for the league"""

    abbr: str = Field(..., description="Abbreviated identifier for the rule.")
    label: str = Field(..., description="Human-readable description of the rule.")
    id: int = Field(..., description="")
    points: float = Field(
        ..., description="How many points are awarded based on the rule."
    )


@dataclass
class LeagueDep:
    """"""

    playoff_matchup_period_length: int
    playoff_seed_tie_rule: str
    scoring_type: str
    matchup_periods: dict = Field(
        ...,
        description="A dictionary where the key is the matchup period, and the value is the list of weeks inside that matchup period.",
    )
    scoring_format: List[ScoringRules] = Field(
        ...,
        description="A list of rules for scoring in the current fantasy football league.",
    )
    regular_season_games_count: int = Field(
        ...,
        description="Number of games in the regular season for the current fantasy football league.",
    )
    position_slots: List[PositionSlot] = Field(
        ..., description="A list containing all eligible slots on my roster."
    )


@dataclass
class WeeklyPlayerProfileDep:
    """Represents a single player's profile and projections for the current fantasy week."""

    name: str = Field(..., description="Player's name.")
    on_bye_week: bool = Field(..., description="True if the player is on bye week.")
    position: str = Field(..., description="Player's professional position.")
    injured: bool = Field(..., description="True if a player is injured.")
    position_rank: List | None = Field(..., description="")

    game_date: Optional[datetime] | None = Field(
        description="The start time of the professional game to be played."
    )
    active_status: str = Field(
        ...,
        description="'active' if a player is available to play in the current week.",
    )
    projected_points: float = Field(
        ..., description="Expected fantasy points for the current week."
    )
    lineup_slot: str = Field(
        ..., description="Current position slot the player occupies."
    )
    eligible_slots: List[str] = Field(
        ..., description="List of position slot names this player can be assigned to."
    )
    professional_opponent: str = Field(
        description="The team the player is going against. "
    )


@dataclass
class MatchupDep:
    is_playoff_match: bool = Field(..., description="True if playoff match.")
    matchup_period: int = Field(
        ..., description="The current match period represented by an integer."
    )
    my_team: List[WeeklyPlayerProfileDep] = Field(
        ...,
        description="List of WeeklyPlayerProfile objects for all players currently on my team.",
    )
    my_team_projected_points: float = Field(
        ...,
        description="The number of points ESPN Fantasy Football thinks my team will score based on the current lineup.",
    )
    opponent_team: List[WeeklyPlayerProfileDep] = Field(
        ...,
        description="List of WeeklyPlayerProfile objects for all players currently on my opponents team.",
    )
    opponent_team_projected_points: float = Field(
        ...,
        description="The number of points ESPN Fantasy Football thinks my opponents team will score based on the current lineup.",
    )
