import asyncio
from typing import Tuple
from dependency_builder import DependencyBuilder
from models import LeagueDep, MatchupDep
from espn_api.football import League
from dotenv import load_dotenv
from agent import run_agent
import os

load_dotenv()

USER_PROMPT = "Evaluate my current fantasy football roster and produce the best possible starting lineup for this week. Recommend any changes and explain your reasoning."

_leagueId = os.getenv("LEAGUE_ID") or 0
_espnS2 = os.getenv("ESPN_S2")
_swid = os.getenv("SWID")
_teamId = 1
_week = 12
_year = 2024


def build_inputs() -> Tuple[LeagueDep, MatchupDep]:
    league: League = League(
        league_id=int(_leagueId), year=_year, espn_s2=_espnS2, swid=_swid
    )

    # _week = league.current_week

    team = league.teams[0]
    box_scores = league.box_scores(_week)

    box_score = next(
        (bs for bs in box_scores if bs.home_team == team or bs.away_team == team)
    )

    if box_score is None:
        quit()

    builder = DependencyBuilder(
        espn_league=league, espn_box_score=box_score, team_id=_teamId
    )

    builder.with_league_dependency().with_matchup_dependency(
        _week
    ).with_betting_odds_data()

    return builder._league_dep, builder._matchup_dep


def main() -> None:
    league_dep, matchup_dep = build_inputs()
    print(league_dep, matchup_dep)
    result = asyncio.run(run_agent(league_dep, matchup_dep, USER_PROMPT))
    print(result)


if __name__ == "__main__":
    main()
