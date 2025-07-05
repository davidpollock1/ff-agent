import asyncio
from dependency_builder import DependencyBuilder
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


def build_inputs():
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

    league_dep = builder.build_league_dependency()
    matchup_dep = builder.build_matchup_dependency()

    return league_dep, matchup_dep


def main():
    league_dep, matchup_dep = build_inputs()
    result = asyncio.run(run_agent(league_dep, matchup_dep, USER_PROMPT))
    print(result)


if __name__ == "__main__":
    main()
