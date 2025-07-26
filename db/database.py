from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from agent.models import LeagueDep, MatchupDep
from datetime import datetime, timedelta
from typing import Tuple
from .models import BettingOdds
from typing import List
import asyncio

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), "TinyDate")

db_lock = asyncio.Lock()
db = TinyDB("sportsbook.json", storage=serialization)
betting_odds_table = db.table("odds")
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


def save_markets(odds: List[BettingOdds]):
    for odd in odds:
        betting_odds_table.insert(odd.model_dump())


async def get_latest_dependencies() -> Tuple[LeagueDep | None, MatchupDep | None]:
    async with db_lock:
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
            latest_matchup_dep = MatchupDep.model_validate(
                matchup_dep[-1]["matchup_dep"]
            )

        return latest_league_dep, latest_matchup_dep


async def get_odds_for_event(event_ids: List[str]) -> List[BettingOdds]:
    async with db_lock:
        query = Query()
        odds = []

        for event_id in event_ids:
            event_odds = betting_odds_table.search(query.event_id == event_id)
            for odd in event_odds:
                market = BettingOdds.model_validate(odd)
                odds.append(market)

        return odds


async def get_odds_for_event_player(event_id: str, player_id: str) -> List[BettingOdds]:
    async with db_lock:
        query = Query()
        odds = []

        event_odds = betting_odds_table.search(
            (query.event_id == event_id) & (query.player_id == player_id)
        )
        for odd in event_odds:
            market = BettingOdds.model_validate(odd)
            odds.append(market)

        return odds
