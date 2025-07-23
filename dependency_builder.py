from typing import List, cast
from espn_api.football import League
from espn_api.football.box_score import BoxScore, BoxPlayer
from espn_api.football.settings import Settings
from clients.sports_odds_api_client import SportsOddsApiClient
from datetime import datetime, timedelta
from models import (
    LeagueDep,
    MatchupDep,
    WeeklyPlayerProfileDep,
    PositionSlot,
    ScoringRules,
)


class DependencyBuilder:
    def __init__(self, espn_league: League, team_id: int) -> None:
        self.espn_league = espn_league
        self.team_id = team_id
        self.odds_api_client = SportsOddsApiClient()
        self._league_dep = LeagueDep()
        self._matchup_dep = MatchupDep()

    def with_league_dependency(self):
        settings = cast(Settings, self.espn_league.settings)
        position_slots: List[PositionSlot] = self.__convert_position_slots(
            settings.position_slot_counts
        )
        scoring_format: List[ScoringRules] = self.__convert_scoring_format(
            settings.scoring_format
        )

        self._league_dep = LeagueDep(
            matchup_periods=settings.matchup_periods,
            scoring_format=scoring_format,
            scoring_type=settings.scoring_type,
            regular_season_games_count=settings.reg_season_count,
            position_slots=position_slots,
            playoff_matchup_period_length=settings.playoff_matchup_period_length,
            playoff_seed_tie_rule=settings.playoff_seed_tie_rule,
        )

        return self

    def with_matchup_dependency(self):
        # box_scores = self.espn_league.box_scores(self.espn_league.current_week)
        box_scores = self.espn_league.box_scores(12)

        team = self.espn_league.teams[self.team_id]

        box_score = next(
            (bs for bs in box_scores if bs.home_team == team or bs.away_team == team)
        )

        if box_score is None:
            return

        is_away = box_score.away_team == self.team_id
        team = box_score.away_lineup if is_away else box_score.home_lineup
        team_projected = (
            box_score.away_projected if is_away else box_score.home_projected
        )
        opponent_projected = (
            box_score.home_projected if is_away else box_score.away_projected
        )

        all_player_ids = [player.playerId for player in team]
        players_result = self.espn_league.player_info(playerId=all_player_ids)

        all_players_info = players_result if isinstance(players_result, list) else []
        player_info_lookup = {
            player.playerId: player.proTeam for player in all_players_info
        }

        team_weekly_player_list = [
            self.__convert_box_player(player, player_info_lookup.get(player.playerId))
            for player in team
        ]

        self._matchup_dep = MatchupDep(
            matchup_period=self.espn_league.current_week,
            is_playoff_match=box_score.is_playoff,
            my_team=team_weekly_player_list,
            my_team_projected_points=team_projected,
            opponent_team_projected_points=opponent_projected,
        )

        return self

    @staticmethod
    def __convert_position_slots(position_slot_counts: dict) -> List[PositionSlot]:
        position_slots = []
        for p, val in position_slot_counts.items():
            if val == 0:
                continue
            is_starting_slot = p not in ("IR", "BE")
            slot = PositionSlot(
                name=p, max_allowed=val, is_starting_slot=is_starting_slot
            )
            position_slots.append(slot)

        return position_slots

    @staticmethod
    def __convert_box_player(box_player: BoxPlayer, pro_team: str | None):
        return WeeklyPlayerProfileDep(
            name=box_player.name,
            active_status=box_player.active_status,
            on_bye_week=box_player.on_bye_week,
            lineup_slot=box_player.lineupSlot,
            position=box_player.position,
            eligible_slots=box_player.eligibleSlots,
            injured=box_player.injured,
            game_date=getattr(box_player, "game_date", None),
            projected_points=box_player.projected_points,
            position_rank=box_player.posRank,
            professional_opponent="",
            professional_team=pro_team,
        )

    @staticmethod
    def __convert_scoring_format(scoring_format: List[dict]) -> List[ScoringRules]:
        return [ScoringRules(**scoring) for scoring in scoring_format]

    @staticmethod
    def __nfl_week_end():
        now = datetime.now()
        days_ahead = (1 - now.weekday() + 7) % 7  # 1 is Tuesday (Monday=0)
        if days_ahead == 0:
            days_ahead = 7
        next_tuesday = now + timedelta(days=days_ahead)
        return next_tuesday.replace(hour=0, minute=1, second=0, microsecond=0)
