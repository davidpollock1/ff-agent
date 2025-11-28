from clients.sports_odds_api_client import SportsOddsApiClient


class IntakeService:
    def __init__(self, sport_odds_api_client: SportsOddsApiClient) -> None:
        self.sports_odds_api_client = SportsOddsApiClient()
