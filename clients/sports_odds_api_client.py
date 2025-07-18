import os
import httpx
from urllib.parse import quote
from datetime import datetime
from .DTOs.odds_api_dtos import NFLEvent, NFLEventResponse, EventOddsResponse

_ODDS_BASE_URL = os.getenv("ODDS_API_BASE_URL")
_ODDS_API_KEY = os.getenv("ODDS_API_KEY")


class SportsOddsApiClient:
    def __init__(self) -> None:
        self.base_url = _ODDS_BASE_URL

    def get_events(
        self, commence_time_from: datetime, commence_time_to: datetime
    ) -> NFLEventResponse:
        iso_commence_time_from = quote(commence_time_from.isoformat() + "Z")
        iso_commence_time_to = quote(commence_time_to.isoformat() + "Z")

        request_url = f"{self.base_url}/v4/sports/americanfootball_nfl/events?apiKey={_ODDS_API_KEY}&dateFormat=iso&commenceTimeFrom={iso_commence_time_from}&commenceTimeTo={iso_commence_time_to}"
        try:
            response = httpx.get(request_url)
            if response.status_code == 200:
                json_data = response.json()
                events = [NFLEvent(**event) for event in json_data]
                return NFLEventResponse(events=events)
        except Exception as e:
            print(f"Error fetching events: {e} ")

        return NFLEventResponse(events=[])

    def get_team_totals_odds_for_event(self, event_id) -> EventOddsResponse:
        bookmaker = "draftkings"
        request_url = f"{self.base_url}/v4/sports/americanfootball_nfl/events/{event_id}/odds?apiKey={_ODDS_API_KEY}&bookmakers={bookmaker}&markets=totals&dateFormat=iso&oddsFormat=american"
        try:
            response = httpx.get(request_url)
            if response.status_code == 200:
                json_data = response.json()
                response = EventOddsResponse(**json_data)
                return response
        except Exception as e:
            print(f"Error fetching totals odds {e}")
        return EventOddsResponse()


# if __name__ == "__main__":
#     sports_odds_client = SportsOddsApiClient()

#     from_time = datetime(2025, 9, 1)
#     to_time = datetime(2025, 9, 16)

#     # response = sports_odds_client.get_events(from_time, to_time)
#     response = sports_odds_client.get_team_totals_odds_for_event(
#         event_id="c6d7807cee33d5e81c671527b9c8b3f1"
#     )
