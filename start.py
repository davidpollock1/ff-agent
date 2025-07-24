import asyncio
from typing import List
from agent.models import LeagueDep, MatchupDep
from db.database import (
    get_latest_dependencies,
    get_latest_event_markets,
    save_league_dep,
    save_matchup_dep,
    save_markets,
)
from db.models import Market
from dependency_builder import DependencyBuilder
from markets_builder import MarketsBuilder
from espn_api.football import League
from dotenv import load_dotenv
from typing import Optional
from agent.agent import run_agent
import os

load_dotenv()

USER_PROMPT = "Evaluate my current fantasy football roster and produce the best possible starting lineup for this week. Recommend any changes and explain your reasoning."

_leagueId = os.getenv("LEAGUE_ID") or 0
_espnS2 = os.getenv("ESPN_S2")
_swid = os.getenv("SWID")
_teamId = 1
_year = 2024  # datetime.now().year


_LEAGUE_DEP: Optional[LeagueDep]
_MATCHUP_DEP: Optional[MatchupDep]
_MARKETS: Optional[List[Market]]


def build_inputs() -> None:
    global _LEAGUE_DEP
    global _MATCHUP_DEP
    global _MARKETS
    try:
        _LEAGUE_DEP, _MATCHUP_DEP = get_latest_dependencies()

        league: League = League(
            league_id=int(_leagueId), year=_year, espn_s2=_espnS2, swid=_swid
        )
        if _LEAGUE_DEP is None or _MATCHUP_DEP is None:
            dep_builder = DependencyBuilder(espn_league=league, team_id=_teamId)
            dep_builder.with_league_dependency().with_matchup_dependency()

            save_league_dep(dep_builder._league_dep)
            save_matchup_dep(dep_builder._matchup_dep)

            _LEAGUE_DEP = dep_builder._league_dep
            _MATCHUP_DEP = dep_builder._matchup_dep

        ids = []
        if _MATCHUP_DEP.team:
            for player in _MATCHUP_DEP.team:
                ids.append(player.event_id)

        _MARKETS = get_latest_event_markets(ids)

        if _MARKETS is None:
            markets_builder = MarketsBuilder(
                _LEAGUE_DEP, _MATCHUP_DEP, league.player_map
            )
            markets_builder.with_player_props_market()
            save_markets(markets_builder._markets)
    except Exception as e:
        print(e)


def main() -> None:
    build_inputs()
    print(_LEAGUE_DEP)
    print("*" * 32)

    print(_MATCHUP_DEP)
    print("*" * 32)

    print(_MARKETS)
    print("*" * 32)
    # result = asyncio.run(run_agent(_LEAGUE_DEP, _MATCHUP_DEP, USER_PROMPT))
    # print(result)


if __name__ == "__main__":
    main()
