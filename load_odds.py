from datetime import datetime
from clients.sports_odds_api_client import SportsOddsApiClient
from db.database import upsert_object
from db.models import NFLEvent
from clients.sports_odds_api_client import NFLEventDTO  # Adjust import if needed
from models import LeagueDep, MatchupDep
from constants import team_map
from typing import Dict


def loadDB(league_dep: LeagueDep, matchup_dep: MatchupDep):
    odds_client = SportsOddsApiClient()
    to_time = datetime(2025, 9, 16)
    from_time = datetime(2025, 9, 1)

    roster = matchup_dep.team or []

    events_response = odds_client.get_events(from_time, to_time)

    event_lookup_by_team: Dict[str, NFLEventDTO] = {}
    if events_response is not None and events_response.events:
        for event in events_response.events:
            event_lookup_by_team[event.home_team] = event
            event_lookup_by_team[event.away_team] = event

    nfl_events = []
    for player in roster:
        if player.active_status == "active":
            pro_team = team_map[player.professional_team or ""]
            event = event_lookup_by_team.get(pro_team)
            if event is not None and event not in nfl_events:
                e = NFLEvent.from_dto(event)
                nfl_events.append(e)

    print(nfl_events)

    for event in nfl_events:
        upsert_object(event, event.id)
