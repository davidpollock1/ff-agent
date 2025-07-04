from datetime import datetime
from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import List, Optional


@dataclass
class LeagueDep:
    matchup_periods: dict
    scoring_format: List[dict]
    scoring_type: str
    regular_season_games_count: int

    position_slot_counts: dict

    playoff_matchup_period_length: int
    playoff_seed_tie_rule: str


@dataclass
class WeeklyPlayerProfileDep:
    name: str
    active_status: str
    on_bye_week: bool
    position: str
    injured: bool
    game_date: Optional[datetime] | None
    projected_points: float

    lineup_slot: str
    eligible_slots: List[str]
    position_rank: List | None


@dataclass
class MatchupDep:
    matchup_period: int
    is_playoff_match: bool

    my_team: List[WeeklyPlayerProfileDep]
    my_team_projected_points: float

    opponent_team: List[WeeklyPlayerProfileDep]
    opponent_team_projected_points: int
