from fastapi import APIRouter
from app.deps import SessionDep, CurrentUserDep
from app.league.schemas import LeagueCreate, LeagueRead
from app.league.service import league_service

router = APIRouter(prefix="/league", tags=["leagues"])


@router.post("/league_config", response_model=LeagueRead, status_code=201)
def create_league_config(
    payload: LeagueCreate, session: SessionDep, current_user: CurrentUserDep
) -> LeagueRead:
    league_config = league_service.create_league(
        session,
        name=payload.name,
        year=payload.year,
        espn_s2=payload.espn_s2,
        swid=payload.swid,
        user=current_user,
    )

    return LeagueRead.model_validate(league_config)


@router.get("/league/{league_id}")
def get_league(league_id: int, session: SessionDep) -> LeagueRead:
    return LeagueRead.model_validate(league_service.get_league(session, league_id))
