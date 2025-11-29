from datetime import datetime, timedelta
from sqlmodel import Session
from clients.sports_odds_api_client import SportsOddsApiClient
from espn_api.football import League
from app.models.models import Event


class IntakeService:
    def __init__(
        self,
        sport_odds_api_client: SportsOddsApiClient,
        espn_league: League,
        session: Session,
    ) -> None:
        self.sports_odds_api_client: SportsOddsApiClient = SportsOddsApiClient()
        self.espn_league = espn_league
        self.session = session

    def fetch_and_store_events(self) -> None:
        events = self.sports_odds_api_client.get_events(
            commence_time_from=datetime.now(),
            commence_time_to=datetime.now() + timedelta(days=7),
        )
        for event in events.events:
            Event(
                id=event.id,
                home_team=event.home_team,
                away_team=event.away_team,
                start_time=datetime.fromisoformat(
                    event.commence_time.replace("Z", "+00:00")
                ),
            )
            self.session.add(event)
        self.session.commit()
