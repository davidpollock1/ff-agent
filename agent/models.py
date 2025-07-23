from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class PositionSlot(BaseModel):
    """A slot on a fantasy football roster."""

    name: str = Field(..., description="Abbreviated name of the roster position slot.")
    max_allowed: int = Field(
        ..., description="Maximum number of players that can occupy this roster slot."
    )
    is_starting_slot: bool = Field(
        ..., description="Whether this slot contributes to weekly scoring."
    )


class ScoringRules(BaseModel):
    """The scoring rules for the league."""

    abbr: str = Field(..., description="Abbreviated identifier for the scoring rule.")
    label: str = Field(
        ..., description="Human-readable description of the scoring rule."
    )
    id: int = Field(..., description="Unique identifier for the scoring rule.")
    points: float = Field(
        ..., description="Point value awarded when this scoring condition is met."
    )


class LeagueDep(BaseModel):
    """League configuration and settings."""

    playoff_matchup_period_length: Optional[int] = Field(
        default=None,
        description="Number of weeks each playoff matchup lasts. Optional; defaults to None.",
    )
    playoff_seed_tie_rule: Optional[str] = Field(
        default=None, description="Tie breaker for playoff seed. "
    )
    scoring_type: Optional[str] = Field(
        default=None, description="Scoring type, like PPR."
    )
    matchup_periods: Optional[dict] = Field(
        default=None,
        description="Mapping of matchup periods to their constituent weeks.",
    )
    scoring_format: Optional[List[ScoringRules]] = Field(
        default=None,
        description="Complete set of scoring rules for this fantasy league.",
    )
    regular_season_games_count: Optional[int] = Field(
        default=None,
        description="Total number of regular season matchups in this league.",
    )
    position_slots: Optional[List[PositionSlot]] = Field(
        default=None, description="Available roster positions and their constraints."
    )


class WeeklyPlayerProfileDep(BaseModel):
    """Represents a single player's profile and projections for the current fantasy week."""

    name: str = Field(..., description="Player's full name.")
    on_bye_week: bool = Field(
        ..., description="Whether the player's NFL team has a bye this week."
    )
    position: str = Field(..., description="Player's primary NFL position.")
    injured: bool = Field(..., description="Whether the player is currently injured.")
    position_rank: List | None = Field(
        ..., description="Player's positional ranking data."
    )

    game_date: Optional[datetime] | None = Field(
        description="Scheduled start time of the player's NFL game."
    )
    active_status: str = Field(
        ...,
        description="Player's roster status ('active' if available to play).",
    )
    projected_points: float = Field(
        ..., description="Forecasted fantasy points for the current week."
    )
    lineup_slot: str = Field(..., description="Current roster position assignment.")
    eligible_slots: List[str] = Field(
        ..., description="Roster positions this player can be assigned to."
    )
    professional_opponent: Optional[str] = Field(
        description="Opposing NFL team for this week's matchup."
    )
    professional_team: Optional[str] = Field(
        description="Current professional team for this player. "
    )


class MatchupDep(BaseModel):
    is_playoff_match: Optional[bool] = Field(
        default=None, description="Whether this is a playoff matchup."
    )
    matchup_period: Optional[int] = Field(
        default=None, description="Current matchup period identifier."
    )
    team: Optional[List[WeeklyPlayerProfileDep]] = Field(
        default=None,
        description="Complete roster of players on the user's fantasy team.",
    )
    team_projected_points: Optional[float] = Field(
        default=None,
        description="Total projected fantasy points for the user's current lineup.",
    )
    opponent_team_projected_points: Optional[float] = Field(
        default=None,
        description="Total projected fantasy points for the opponent's current lineup.",
    )
