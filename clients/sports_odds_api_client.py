import os
from typing import Set
import httpx
from urllib.parse import quote
from datetime import datetime
from .DTOs.odds_api_dtos import NFLEventDTO, NFLEventResponseDTO, EventOddsResponseDTO
import logging

logger = logging.getLogger(__name__)

_ODDS_BASE_URL = os.getenv("ODDS_API_BASE_URL")
_ODDS_API_KEY = os.getenv("ODDS_API_KEY")


class SportsOddsApiClient:
    def __init__(self) -> None:
        self.base_url = _ODDS_BASE_URL
        self.sport_key = "americanfootball_nfl"

    def get_events(
        self, commence_time_from: datetime, commence_time_to: datetime
    ) -> NFLEventResponseDTO:
        iso_commence_time_from = quote(commence_time_from.isoformat() + "Z")
        iso_commence_time_to = quote(commence_time_to.isoformat() + "Z")

        request_url = f"{self.base_url}/v4/sports/{self.sport_key}/events?apiKey={_ODDS_API_KEY}&dateFormat=iso&commenceTimeFrom={iso_commence_time_from}&commenceTimeTo={iso_commence_time_to}"
        try:
            response = httpx.get(request_url)
            if response.status_code == 200:
                json_data = response.json()
                events = [NFLEventDTO(**event) for event in json_data]
                return NFLEventResponseDTO(events=events)
        except Exception as e:
            logger.error(f"Error fetching events: {e} ")

        return NFLEventResponseDTO(events=[])

    def get_team_totals_odds_for_event(self, event_id: str) -> EventOddsResponseDTO:
        bookmaker = "draftkings"
        request_url = f"{self.base_url}/v4/sports/{self.sport_key}/events/{event_id}/odds?apiKey={_ODDS_API_KEY}&bookmakers={bookmaker}&markets=totals&dateFormat=iso&oddsFormat=american"
        try:
            response = httpx.get(request_url)
            if response.status_code == 200:
                json_data = response.json()
                response = EventOddsResponseDTO(**json_data)
                return response
        except Exception as e:
            logger.error(f"Error fetching totals odds {e}")
        return EventOddsResponseDTO()

    def get_player_props_odds_for_event(
        self, event_id: str, market_ids: Set[str]
    ) -> EventOddsResponseDTO:
        bookmaker = "draftkings"
        markets_param = ",".join(market_ids)
        request_url = f"{self.base_url}/v4/sports/{self.sport_key}/events/{event_id}/odds?apiKey={_ODDS_API_KEY}&bookmakers={bookmaker}&markets={markets_param}&dateFormat=iso&oddsFormat=american"
        try:
            response = httpx.get(request_url)
            if response.status_code == 200:
                json_data = response.json()
                response = EventOddsResponseDTO(**json_data)
                return response
        except Exception as e:
            logger.error(f"Error fetching totals odds {e}")
        return EventOddsResponseDTO()
