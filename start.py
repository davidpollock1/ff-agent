import asyncio
from typing import Tuple
from db.database import get_latest_dependencies
from dependency_builder import DependencyBuilder
from agent.models import LeagueDep, MatchupDep
from espn_api.football import League
from dotenv import load_dotenv
from agent.agent import run_agent
from load_odds import loadDB, save_dependencies
import os

load_dotenv()

USER_PROMPT = "Evaluate my current fantasy football roster and produce the best possible starting lineup for this week. Recommend any changes and explain your reasoning."

_leagueId = os.getenv("LEAGUE_ID") or 0
_espnS2 = os.getenv("ESPN_S2")
_swid = os.getenv("SWID")
_teamId = 1
_week = 12
_year = 2024  # datetime.now().year


def build_inputs() -> Tuple[LeagueDep, MatchupDep]:
    league_dep, matchup_dep = get_latest_dependencies()

    if league_dep is not None and matchup_dep is not None:
        return league_dep, matchup_dep

    league: League = League(
        league_id=int(_leagueId), year=_year, espn_s2=_espnS2, swid=_swid
    )

    # _week = league.current_week

    builder = DependencyBuilder(espn_league=league, team_id=_teamId)

    builder.with_league_dependency().with_matchup_dependency()

    loadDB(builder._league_dep, builder._matchup_dep)
    save_dependencies(builder._league_dep, builder._matchup_dep)
    return builder._league_dep, builder._matchup_dep


def main() -> None:
    league_dep, matchup_dep = build_inputs()

    print(league_dep, matchup_dep)
    # result = asyncio.run(run_agent(league_dep, matchup_dep, USER_PROMPT))
    # print(result)


if __name__ == "__main__":
    main()
