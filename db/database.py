from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from agent.models import LeagueDep, MatchupDep
from datetime import datetime, timedelta
from typing import Tuple
from .models import Market
from typing import List

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), "TinyDate")

db = TinyDB("sportsbook.json", storage=serialization)
markets_table = db.table("markets")
league_dependency_table = db.table("league_dependency")
matchup_dependency_table = db.table("matchup_dependency")


# def save_event(event: Event):
#     EventQ = Query()
#     events_table.upsert(event.model_dump(), EventQ.event_id == event.id)


def save_league_dep(league_dep: LeagueDep):
    league_dependency_table.insert(
        {"timestamp": datetime.now(), "league_dep": league_dep.model_dump()}
    )


def save_matchup_dep(matchup_dep: MatchupDep):
    matchup_dependency_table.insert(
        {
            "timestamp": datetime.now(),
            "matchup_dep": matchup_dep.model_dump(),
        }
    )


def save_markets(markets: List[Market]):
    for market in markets:
        markets_table.insert(
            {
                "timestamp": datetime.now(),
                "market": market.model_dump(),
            }
        )


def get_latest_dependencies() -> Tuple[LeagueDep | None, MatchupDep | None]:
    query = Query()
    league_dep = league_dependency_table.search(
        query.timestamp > datetime.now() - timedelta(days=2)
    )
    matchup_dep = matchup_dependency_table.search(
        query.timestamp > datetime.now() - timedelta(days=2)
    )

    latest_league_dep = None
    latest_matchup_dep = None

    if league_dep:
        latest_league_dep = LeagueDep.model_validate(league_dep[-1]["league_dep"])
    if matchup_dep:
        latest_matchup_dep = MatchupDep.model_validate(matchup_dep[-1]["matchup_dep"])

    return latest_league_dep, latest_matchup_dep


def get_latest_event_markets(event_ids: List[str]) -> List[Market]:
    query = Query()
    markets = []

    for event_id in event_ids:
        event_markets = markets_table.search(query.market["event_id"] == event_id)
        for market_entry in event_markets:
            market_data = market_entry["market"]

            market = Market.model_validate(market_data)
            markets.append(market)

    return markets
