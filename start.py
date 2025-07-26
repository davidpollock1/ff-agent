import asyncio
import os
import logging
import logger_config
from typing import List
from typing import Optional

from db.database import (
    get_latest_dependencies,
    get_odds_for_event,
    get_odds_for_event_player,
    save_league_dep,
    save_matchup_dep,
    save_markets,
)
from db.models import BettingOdds
from dependency_builder import DependencyBuilder
from markets_builder import MarketsBuilder
from espn_api.football import League
from dotenv import load_dotenv
from agent.models import LeagueDep, MatchupDep
from agent.agent import run_agent

logger = logging.getLogger(__name__)

load_dotenv()

USER_PROMPT = "Build the optimal starting lineup for this week. Maximize projected points, follow roster rules, and summarize the key changes made compared to the current lineup."

_leagueId = os.getenv("LEAGUE_ID") or 0
_espnS2 = os.getenv("ESPN_S2")
_swid = os.getenv("SWID")
_teamId = 1
_year = 2025  # datetime.now().year


_LEAGUE_DEP: Optional[LeagueDep]
_MATCHUP_DEP: Optional[MatchupDep]
_MARKETS: Optional[List[BettingOdds]]


async def build_inputs() -> None:
    global _LEAGUE_DEP
    global _MATCHUP_DEP
    global _MARKETS
    try:
        logger.info("Building inputs.")
        _LEAGUE_DEP, _MATCHUP_DEP = await get_latest_dependencies()

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

        _MARKETS = await get_odds_for_event(ids)

        if len(_MARKETS) <= 0:
            markets_builder = MarketsBuilder(
                _LEAGUE_DEP, _MATCHUP_DEP, league.player_map
            )
            markets_builder.with_totals_market().with_player_props_market()
            save_markets(markets_builder._betting_odds)
            _MARKETS = await get_odds_for_event(ids)
    except Exception as e:
        logger.error(e)


async def main() -> None:
    await build_inputs()
    # event_id = "f1bc532dff946d15cb85654b5c4b246e"
    # player_id = "4361579"
    # # print(await get_odds_for_event_player(event_id, player_id))
    # result = await run_agent(_LEAGUE_DEP, _MATCHUP_DEP, USER_PROMPT)
    # print(result)5


if __name__ == "__main__":
    asyncio.run(main())
