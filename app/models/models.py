import datetime
from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Field
from app.models.user import User  # noqa: F401
from uuid import UUID


class Event(SQLModel, table=True):
    id: int = Field(primary_key=True)
    home_team: str
    away_team: str
    start_time: datetime.datetime


class Team(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    provider_team_id: str
    name: str
    owner: str

    league_id: int = Field(foreign_key="league.id")
    league: Optional["League"] = Relationship(back_populates="teams")

    team_weeks: Optional[List["TeamWeek"]] = Relationship(back_populates="team")


class LeaguePositionSlot(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    max_allowed: int
    is_starting_slot: bool

    league_id: int = Field(foreign_key="league.id")
    league: Optional["League"] = Relationship(back_populates="position_slots")


class League(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    provider_league_id: str
    name: str | None = None
    year: int | None = None
    espn_s2: str | None = None
    swid: str | None = None
    scoring_type: str | None = None
    teams: Optional[List[Team]] = Relationship(back_populates="league")
    position_slots: Optional[List[LeaguePositionSlot]] = Relationship(
        back_populates="league"
    )


class TeamWeek(SQLModel, table=True):
    id: int = Field(primary_key=True)
    team_id: int = Field(foreign_key="team.id")
    week: int
    team: Optional["Team"] = Relationship(back_populates="team_weeks")
    players: Optional[List["TeamWeekPlayer"]] = Relationship(back_populates="team_week")


class TeamWeekPlayer(SQLModel, table=True):
    id: int = Field(primary_key=True)
    team_week_id: int = Field(foreign_key="teamweek.id")
    team_week: Optional["TeamWeek"] = Relationship(back_populates="players")

    player_week_id: int = Field(foreign_key="playerweek.id")
    player_week: Optional["PlayerWeek"] = Relationship(
        back_populates="team_week_player"
    )


class PlayerWeek(SQLModel, table=True):
    id: int = Field(primary_key=True)
    professional_team_opponent: str
    projected_points: float
    event_id: str | None = None
    player_id: int = Field(foreign_key="player.id")
    player: Optional["Player"] = Relationship()
    team_week_player: Optional["TeamWeekPlayer"] = Relationship(
        back_populates="player_week"
    )


class Player(SQLModel, table=True):
    id: int = Field(primary_key=True)
    provider_player_id: str
    name: str
    position: str
    professional_team: str
