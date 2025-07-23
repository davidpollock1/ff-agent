from datetime import datetime
from clients.sports_odds_api_client import SportsOddsApiClient
from clients.sports_odds_api_client import NFLEventDTO  # Adjust import if needed
from agent.models import LeagueDep, MatchupDep
from constants import team_map
from typing import Dict, List
from db.database import save_event, save_league_dep, save_matchup_dep
from db.models import Event


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
        if player.active_status != "active":
            continue

        pro_team = team_map[player.professional_team or ""]
        event = event_lookup_by_team.get(pro_team)
        if event is None:
            continue

        player.event_id = event.id
        if event not in nfl_events:
            events_odds_response = odds_client.get_team_totals_odds_for_event(
                event_id=event.id
            )
            nfl_events.append(Event.from_event_odds_response_dto(events_odds_response))

    for event in nfl_events:
        save_event(event)


def save_dependencies(league_dep: LeagueDep, matchup_dep: MatchupDep):
    save_league_dep(league_dep)
    save_matchup_dep(matchup_dep)


class EventsBuilder:
    def __init__(
        self,
        odds_api_client: SportsOddsApiClient,
        league_dep: LeagueDep,
        matchup_dep: MatchupDep,
    ) -> None:
        self.odds_api_client = odds_api_client
        self.league_dep = league_dep
        self.matchup_dep = matchup_dep
        self.events = List[Event()]

    def build_events(self):
        to_time = datetime(2025, 9, 16)
        from_time = datetime(2025, 9, 1)

        roster = self.matchup_dep.team or []

        events_response = self.odds_api_client.get_events(from_time, to_time)

        event_lookup_by_team: Dict[str, NFLEventDTO] = {}
        if events_response is not None and events_response.events:
            for event in events_response.events:
                event_lookup_by_team[event.home_team] = event
                event_lookup_by_team[event.away_team] = event

        nfl_events = []
        for player in roster:
            if player.active_status != "active":
                continue

            pro_team = team_map[player.professional_team or ""]
            event = event_lookup_by_team.get(pro_team)
            if event is None:
                continue

            player.event_id = event.id
            if event not in nfl_events:
                events_odds_response = (
                    self.odds_api_client.get_team_totals_odds_for_event(
                        event_id=event.id
                    )
                )
                nfl_events.append(
                    Event.from_event_odds_response_dto(events_odds_response)
                )

        self.events = nfl_events

        for event in nfl_events:
            save_event(event)
