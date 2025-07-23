from datetime import datetime
from clients.sports_odds_api_client import SportsOddsApiClient
from db.database import create_db_and_tables, get_session
from db.models import NFLEvent
from models import LeagueDep, MatchupDep


def loadDB(league_dep: LeagueDep, matchup_dep: MatchupDep):
    odds_client = SportsOddsApiClient()
    to_time = datetime(2025, 9, 16)
    from_time = datetime(2025, 9, 1)

    events_response = odds_client.get_events(from_time, to_time)

    print(events_response)
    create_db_and_tables()

    session = get_session()

    with session:
        for event in events_response.events:
            e = NFLEvent.from_dto(event)
            session.add(e)

        session.commit()
