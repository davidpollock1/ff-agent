from fastapi import APIRouter
from app.deps import SessionDep, CurrentUserDep
from app.league.schemas import (
    LeagueCreate,
    LeagueRead,
    LeagueWithTeamRead,
    LeagueWithTeamCreate,
    TeamRead,
    SyncTeamWeek,
)
from app.league.service import league_service

router = APIRouter(prefix="/league", tags=["leagues"])


@router.post("/league_config", response_model=LeagueRead, status_code=201)
def create_league_config(
    data: LeagueCreate, session: SessionDep, current_user: CurrentUserDep
) -> LeagueRead:
    league_config = league_service.create_league(
        session,
        provider_league_id=data.provider_league_id,
        name=data.name,
        year=data.year,
        espn_s2=data.espn_s2,
        swid=data.swid,
        user=current_user,
    )

    return LeagueRead.model_validate(league_config)


@router.post("/league/team", response_model=LeagueWithTeamRead, status_code=201)
def create_league_team(
    data: LeagueWithTeamCreate, session: SessionDep, current_user: CurrentUserDep
) -> LeagueWithTeamRead:
    league, team = league_service.create_league_team(
        session=session,
        provider_league_id=data.league.provider_league_id,
        name=data.league.name,
        year=data.league.year,
        espn_s2=data.league.espn_s2,
        swid=data.league.swid,
        provider_team_id=data.team.provider_team_id,
        user=current_user,
    )
    league_read = LeagueRead.model_validate(league)
    team_read = TeamRead.model_validate(team)

    return LeagueWithTeamRead(league=league_read, team=team_read)


@router.get("/{league_id}", response_model=LeagueRead)
def get_league(league_id: int, session: SessionDep) -> LeagueRead:
    return LeagueRead.model_validate(league_service.get_league(session, league_id))


@router.post("/teamweek/sync/")
def sync_league(data: SyncTeamWeek, session: SessionDep) -> bool:
    return league_service.sync_team_week(session, data.team_id, data.week)
