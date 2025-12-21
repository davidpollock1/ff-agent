from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class LeagueCreate(BaseModel):
    name: str
    provider_league_id: str
    espn_s2: str
    swid: str
    year: int


class LeagueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider_league_id: str
    user_id: UUID
    name: str
    year: int
    espn_s2: str
    swid: str


class TeamCreate(BaseModel):
    name: Optional[str] = None
    provider_team_id: int
    user_id: Optional[UUID] = None
    league_id: Optional[int] = None


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    provider_team_id: int
    user_id: Optional[UUID] = None
    league_id: Optional[int] = None


class LeagueWithTeamCreate(BaseModel):
    league: LeagueCreate
    team: TeamCreate


class LeagueWithTeamRead(BaseModel):
    league: LeagueRead
    team: TeamRead


class SyncTeamWeek(BaseModel):
    team_id: int
    week: int
