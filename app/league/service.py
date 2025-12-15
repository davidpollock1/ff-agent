from sqlmodel import Session, select
from app.models.models import League, Team
from app.models.user import User
from app.integrations.espn.client import EspnClient


class LeagueService:
    def __init__(self, espn: EspnClient) -> None:
        self._espn = espn

    def create_league(
        self,
        session: Session,
        *,
        espn_league_id: str,
        name: str,
        year: int,
        espn_s2: str,
        swid: str,
        user: User,
    ) -> League:
        league = League(
            name=name,
            espn_league_id=espn_league_id,
            year=year,
            espn_s2=espn_s2,
            swid=swid,
            user_id=user.id,
        )

        session.add(league)
        session.commit()
        session.refresh(league)

        return league

    def create_league_team(
        self,
        session: Session,
        *,
        espn_league_id: str,
        name: str,
        year: int,
        espn_s2: str,
        swid: str,
        team_id: int,
        user: User,
    ) -> tuple[League, Team]:
        league = self.create_league(
            session=session,
            espn_league_id=espn_league_id,
            name=name,
            year=year,
            espn_s2=espn_s2,
            swid=swid,
            user=user,
        )
        session.flush()

        espn_league = self._espn.get_league(
            league_id=league.espn_league_id,
            year=league.year,
            espn_s2=league.espn_s2,
            swid=league.swid,
        )

        espn_team = espn_league.teams[team_id]

        team = Team(
            league_id=league.id,
            user_id=user.id,
            name=espn_team.team_name,
            owner=espn_team.owners[0].get("displayName"),
            espn_team_id=espn_team.team_id,
            espn_league_id=league.espn_league_id,
        )

        session.add(team)
        session.commit()
        session.refresh(league)

        return league, team

    def get_league(self, session: Session, id: int) -> League | None:
        return session.exec(select(League).where(League.id == id)).first()

    def sync_league(self, session: Session, id: int) -> League | None:
        league = self.get_league(session, id)
        if not league:
            return None

        espn_league = self._espn.get_league(
            league_id=league.espn_league_id,
            year=league.year,
            espn_s2=league.espn_s2,
            swid=league.swid,
        )

        return league


league_service = LeagueService(EspnClient())
