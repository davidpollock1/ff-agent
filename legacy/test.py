from datetime import datetime
import os
from dotenv import load_dotenv
from espn_api.football import League

load_dotenv()

_leagueId = os.getenv("LEAGUE_ID") or 0
_espnS2 = os.getenv("ESPN_S2")
_swid = os.getenv("SWID")
_teamId = 0
_year = datetime.now().year


def get_league() -> League:
    league = League(league_id=_leagueId, year=_year, espn_s2=_espnS2, swid=_swid)
    return league


if __name__ == "__main__":
    league = get_league()

    boxscore = league.box_scores(week=1)

    team = boxscore[0].home_lineup

    for player in team:
        print(player)
    print(league.teams)
