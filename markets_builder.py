from collections import defaultdict
from clients.sports_odds_api_client import SportsOddsApiClient
from agent.models import LeagueDep, MatchupDep
from typing import Dict, List, Set
from db.models import Market
from constants import position_markets_map

EventMarketsMap = Dict[str, Set[str]]


class MarketsBuilder:
    def __init__(
        self,
        league_dep: LeagueDep,
        matchup_dep: MatchupDep,
        player_map: Dict,
    ) -> None:
        self.odds_api_client = SportsOddsApiClient()
        self.player_map = player_map
        self.league_dep = league_dep
        self.matchup_dep = matchup_dep
        self._markets: List[Market] = []

    def with_totals_market(self):
        roster = self.matchup_dep.team or []

        for player in roster:
            if player.active_status != "active":
                continue
            if player.event_id is None:
                continue

            events_odds_response = self.odds_api_client.get_team_totals_odds_for_event(
                event_id=player.event_id
            )
            self._markets.extend(
                Market.from_event_odds_response_dto(events_odds_response)
            )

        return self

    def with_player_props_market(self):
        roster = self.matchup_dep.team or []
        event_id_to_markets: EventMarketsMap = defaultdict(set)

        markets = []
        for player in roster:
            if player.active_status != "active":
                continue
            if player.event_id is None:
                continue

            market_ids_for_position = position_markets_map[player.position]
            event_id_to_markets[player.event_id].update(market_ids_for_position)

        for event_id, market_ids in event_id_to_markets.items():
            events_odds_response = self.odds_api_client.get_player_props_odds_for_event(
                event_id, market_ids=market_ids
            )
            self._markets.extend(
                Market.from_event_odds_response_dto(events_odds_response)
            )
            break  # only calling odds api for first loop, conserving free calls.
