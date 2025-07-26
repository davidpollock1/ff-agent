from typing import Dict, List, Tuple, cast
from espn_api.football import League
from espn_api.football.box_score import BoxPlayer
from espn_api.football.settings import Settings
from clients.sports_odds_api_client import SportsOddsApiClient
from datetime import datetime, timedelta
from constants import team_map
from agent.models import (
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
        current_week = self.espn_league.current_week
        box_scores = self.espn_league.box_scores(current_week)
        team = self.espn_league.teams[self.team_id]

        box_score = next(
            (bs for bs in box_scores if bs.home_team == team or bs.away_team == team)
        )

        if box_score is None:
            return

        is_away = box_score.away_team == team
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

        from_time, to_time = self.__get_nfl_week_range(current_week)
        events_response = self.odds_api_client.get_events(from_time, to_time)

        event_lookup_by_team: Dict[str, str] = {}
        if events_response is not None and events_response.events:
            for event in events_response.events:
                event_lookup_by_team[event.home_team] = event.id
                event_lookup_by_team[event.away_team] = event.id

        team_weekly_player_list = []
        for player in team:
            team_abbr = player_info_lookup.get(player.playerId, "Unknown Team")
            event_id = event_lookup_by_team.get(team_map[team_abbr], "Unknown Event")
            wp = self.__convert_box_player(player, team_abbr, event_id)
            team_weekly_player_list.append(wp)

        self._matchup_dep = MatchupDep(
            matchup_period=self.espn_league.current_week,
            is_playoff_match=box_score.is_playoff,
            team=team_weekly_player_list,
            team_projected_points=team_projected,
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
    def __convert_box_player(
        box_player: BoxPlayer, pro_team: str | None, event_id: str
    ) -> WeeklyPlayerProfileDep:
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
            professional_opponent=box_player.pro_opponent,
            professional_team=pro_team,
            event_id=event_id,
            player_id=str(box_player.playerId),
        )

    @staticmethod
    def __convert_scoring_format(scoring_format: List[dict]) -> List[ScoringRules]:
        return [ScoringRules(**scoring) for scoring in scoring_format]

    @staticmethod
    def __get_nfl_week_range(current_week: int) -> Tuple[datetime, datetime]:
        season_start = datetime(2025, 9, 4)
        if current_week < 1:
            raise ValueError("current_week must be 1 or greater")

        week_start = season_start + timedelta(weeks=(1 - 1))
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
