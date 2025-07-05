from typing import cast
from espn_api.football import League
from espn_api.football.settings import Settings
from dotenv import load_dotenv
from models import LeagueDep, MatchupDep, WeeklyPlayerProfileDep
import os

load_dotenv()

_leagueId = os.getenv("LEAGUE_ID") or 0
_espnS2 = os.getenv("ESPN_S2")
_swid = os.getenv("SWID")
_teamId = 1
_matchupPeriod = 12

league: League = League(
    league_id=int(_leagueId), year=2024, espn_s2=_espnS2, swid=_swid
)

settings = league.settings
print(league)
settings.scoring_format
league.box_scores(1)


def get_league_dep():
    settings = cast(Settings, league.settings)

    league_dep = LeagueDep(
        matchup_periods=settings.matchup_periods,
        scoring_format=settings.scoring_format,
        scoring_type=settings.scoring_type,
        regular_season_games_count=settings.reg_season_count,
        position_slots=[],
        playoff_matchup_period_length=settings.playoff_matchup_period_length,
        playoff_seed_tie_rule=settings.playoff_seed_tie_rule,
    )

    return league_dep


# def get_matchup_dep():
#     # TODO: Better team selection logic.
#     team = league.teams[0]

#     box_scores = league.box_scores(_matchupPeriod)
#     box_score = next(
#         (bs for bs in box_scores if bs.home_team == team or bs.away_team == team)
#     )
#     if box_scores is None:
#         quit()

#     if box_score.away_team == _teamId:
#         team = box_score.away_lineup
#         opponent = box_score.home_lineup
#     else:
#         opponent = box_score.away_lineup
#         team = box_score.home_lineup

#     team_weekly_player_list = [
#         WeeklyPlayerProfileDep(
#             name=player.name,
#             active_status=player.active_status,
#             on_bye_week=player.on_bye_week,
#             lineup_slot=player.lineupSlot,
#             position=player.position,
#             eligible_slots=player.eligibleSlots,
#             injured=player.injured,
#             game_date=getattr(player, "game_date", None),
#             projected_points=player.projected_points,
#             position_rank=player.posRank or None,
#         )
#         for player in team
#     ]

#     opponent_weekly_player_list = [
#         WeeklyPlayerProfileDep(
#             name=player.name,
#             active_status=player.active_status,
#             on_bye_week=player.on_bye_week,
#             lineup_slot=player.lineupSlot,
#             position=player.position,
#             eligible_slots=player.eligibleSlots,
#             injured=player.injured,
#             game_date=getattr(player, "game_date", None),
#             projected_points=player.projected_points,
#             position_rank=player.posRank,
#         )
#         for player in opponent
#     ]

#     matchup_dep = MatchupDep(
#         matchup_period=_matchupPeriod,
#         is_playoff_match=box_score.is_playoff,
#         my_team=team_weekly_player_list,
#         my_team_projected_points=0,
#         opponent_team=opponent_weekly_player_list,
#         opponent_team_projected_points=0,
#     )

#     return matchup_dep
