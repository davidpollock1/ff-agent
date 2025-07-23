import asyncio
from db.database import (
    get_latest_dependencies,
    save_league_dep,
    save_matchup_dep,
    save_markets,
)
from dependency_builder import DependencyBuilder
from markets_builder import MarketsBuilder
from espn_api.football import League
from dotenv import load_dotenv
from agent.agent import run_agent
import os

load_dotenv()

USER_PROMPT = "Evaluate my current fantasy football roster and produce the best possible starting lineup for this week. Recommend any changes and explain your reasoning."

_leagueId = os.getenv("LEAGUE_ID") or 0
_espnS2 = os.getenv("ESPN_S2")
_swid = os.getenv("SWID")
_teamId = 1
_year = 2024  # datetime.now().year

_LEAGUE_DEP = None
_MATCHUP_DEP = None
_MARKETS = None


def build_inputs() -> None:
    _LEAGUE_DEP, _MATCHUP_DEP = get_latest_dependencies()

    if _LEAGUE_DEP is None or _MATCHUP_DEP is None:
        league: League = League(
            league_id=int(_leagueId), year=_year, espn_s2=_espnS2, swid=_swid
        )
        dep_builder = DependencyBuilder(espn_league=league, team_id=_teamId)
        dep_builder.with_league_dependency().with_matchup_dependency()

        if _MARKETS is None:
            markets_builder = MarketsBuilder(
                dep_builder._league_dep, dep_builder._matchup_dep, league.player_map
            )
            markets_builder.with_player_props_market()
            markets = markets_builder._markets
            save_markets(markets)

        save_league_dep(dep_builder._league_dep)
        save_matchup_dep(dep_builder._matchup_dep)


def main() -> None:
    build_inputs()

    # print(_LEAGUE_DEP, _MATCHUP_DEP)
    # result = asyncio.run(run_agent(_LEAGUE_DEP, _MATCHUP_DEP, USER_PROMPT))
    # print(result)


if __name__ == "__main__":
    main()
