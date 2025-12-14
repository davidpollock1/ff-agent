from sqlmodel import Session, select
from app.models.models import League
from app.models.user import User


class LeagueService:
    def __init__(self) -> None:
        pass

    def create_league(
        self,
        session: Session,
        *,
        name: str,
        year: int,
        espn_s2: str,
        swid: str,
        user: User,
    ) -> League:
        league = League(
            name=name,
            year=year,
            espn_s2=espn_s2,
            swid=swid,
        )

        session.add(league)
        session.commit()
        session.refresh(league)

        return league

    def get_league(self, session: Session, id: int) -> League | None:
        return session.exec(select(League).where(League.id == id)).first()


league_service = LeagueService()
