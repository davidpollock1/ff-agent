import datetime
from sqlmodel import SQLModel, Field


# User model for authentication
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )


class Event(SQLModel, table=True):
    id: str = Field(primary_key=True)
    home_team: str
    away_team: str
    start_time: datetime.datetime


class League(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    scoring_type: str
    year: int
    espn_s2: str
    swid: str


class Team(SQLModel, table=True):
    id: int = Field(primary_key=True)
    league_id: int = Field(foreign_key="league.id")
    name: str
    owner: str


class LeaguePositionSlot(SQLModel, table=True):
    id: int = Field(primary_key=True)
    league_id: int = Field(foreign_key="league.id")
    name: str
    max_allowed: int
    is_starting_slot: bool


class TeamWeek(SQLModel, table=True):
    id: int = Field(primary_key=True)
    team_id: int = Field(foreign_key="team.id")
    week: int


class TeamWeekPlayer(SQLModel, table=True):
    id: int = Field(primary_key=True)
    team_week_id: int = Field(foreign_key="teamweek.id")
    player_id: int = Field(foreign_key="playerweek.id")


class PlayerWeek(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    position: str
    professional_team: str
    professional_team_opponent: str
    projected_points: float
    event_id: str
