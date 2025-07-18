from typing import List, cast
from espn_api.football import League
from espn_api.football.box_score import BoxScore, BoxPlayer
from espn_api.football.settings import Settings
from models import (
    LeagueDep,
    MatchupDep,
    WeeklyPlayerProfileDep,
    PositionSlot,
    ScoringRules,
)


class DependencyBuilder:
    def __init__(
        self, espn_league: League, espn_box_score: BoxScore, team_id: int
    ) -> None:
        self.espn_league = espn_league
        self.box_score = espn_box_score
        self.team_id = team_id

    def build_league_dependency(self) -> LeagueDep:
        settings = cast(Settings, self.espn_league.settings)
        position_slots: List[PositionSlot] = self.__convert_position_slots(
            settings.position_slot_counts
        )
        scoring_format: List[ScoringRules] = self.__convert_scoring_format(
            settings.scoring_format
        )

        league_dep = LeagueDep(
            matchup_periods=settings.matchup_periods,
            scoring_format=scoring_format,
            scoring_type=settings.scoring_type,
            regular_season_games_count=settings.reg_season_count,
            position_slots=position_slots,
            playoff_matchup_period_length=settings.playoff_matchup_period_length,
            playoff_seed_tie_rule=settings.playoff_seed_tie_rule,
        )

        return league_dep

    def build_matchup_dependency(self, week: int) -> MatchupDep:
        if self.box_score is None:
            quit()

        is_away = self.box_score.away_team == self.team_id
        team = self.box_score.away_lineup if is_away else self.box_score.home_lineup
        team_projected = (
            self.box_score.away_projected if is_away else self.box_score.home_projected
        )
        opponent = self.box_score.home_lineup if is_away else self.box_score.away_lineup
        opponent_projected = (
            self.box_score.home_projected if is_away else self.box_score.away_projected
        )

        all_player_ids = [player.playerId for player in team + opponent]
        players_result = self.espn_league.player_info(playerId=all_player_ids)

        all_players_info = players_result if isinstance(players_result, list) else []
        player_info_lookup = {
            player.playerId: player.proTeam for player in all_players_info
        }

        team_weekly_player_list = [
            self.__convert_box_player(player, player_info_lookup.get(player.playerId))
            for player in team
        ]

        opponent_weekly_player_list = [
            self.__convert_box_player(player, player_info_lookup.get(player.playerId))
            for player in opponent
        ]

        matchup_dep = MatchupDep(
            matchup_period=week,
            is_playoff_match=self.box_score.is_playoff,
            my_team=team_weekly_player_list,
            my_team_projected_points=team_projected,
            opponent_team=opponent_weekly_player_list,
            opponent_team_projected_points=opponent_projected,
        )

        return matchup_dep

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
            profession_team=pro_team,
        )

    @staticmethod
    def __convert_scoring_format(scoring_format: List[dict]) -> List[ScoringRules]:
        return [ScoringRules(**scoring) for scoring in scoring_format]
