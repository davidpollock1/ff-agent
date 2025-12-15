import datetime
from sqlmodel import SQLModel, Field
from app.models.user import User  # noqa: F401
from uuid import UUID


class Event(SQLModel, table=True):
    id: str = Field(primary_key=True)
    home_team: str
    away_team: str
    start_time: datetime.datetime


class League(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    espn_league_id: str
    name: str | None = None
    year: int
    espn_s2: str
    swid: str
    scoring_type: str | None = None


class Team(SQLModel, table=True):
    id: int = Field(primary_key=True)
    league_id: int = Field(foreign_key="league.id")
    user_id: UUID = Field(foreign_key="user.id")
    espn_team_id: int
    espn_league_id: str
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
