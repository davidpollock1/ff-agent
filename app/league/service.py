from datetime import datetime
from sqlmodel import Session, select
from app.models.models import League, Team, TeamWeek, TeamWeekPlayer
from app.models.user import User
from app.integrations.espn.client import EspnClient
from sqlalchemy.dialects.postgresql import insert


class LeagueService:
    def __init__(self, espn: EspnClient) -> None:
        self._espn = espn

    def create_league(
        self,
        session: Session,
        *,
        espn_league_id: str,
        name: str,
        year: int,
        espn_s2: str,
        swid: str,
        user: User,
    ) -> League:
        league = League(
            name=name,
            espn_league_id=espn_league_id,
            year=year,
            espn_s2=espn_s2,
            swid=swid,
            user_id=user.id,
        )

        session.add(league)
        session.commit()
        session.refresh(league)

        return league

    def create_league_team(
        self,
        session: Session,
        *,
        espn_league_id: str,
        name: str,
        year: int,
        espn_s2: str,
        swid: str,
        team_id: int,
        user: User,
    ) -> tuple[League, Team]:
        league = self.create_league(
            session=session,
            espn_league_id=espn_league_id,
            name=name,
            year=year,
            espn_s2=espn_s2,
            swid=swid,
            user=user,
        )
        session.flush()

        espn_league = self._espn.get_league(
            league_id=league.espn_league_id,
            year=league.year,
            espn_s2=league.espn_s2,
            swid=league.swid,
        )

        espn_team = espn_league.teams[team_id]

        team = Team(
            league_id=league.id,
            user_id=user.id,
            name=espn_team.team_name,
            owner=espn_team.owners[0].get("displayName"),
            espn_team_id=espn_team.team_id,
            espn_league_id=league.espn_league_id,
        )

        session.add(team)
        session.commit()
        session.refresh(league)

        return league, team

    def get_league(self, session: Session, id: int) -> League | None:
        return session.exec(select(League).where(League.id == id)).first()

    # TODO: Refactor
    def sync_team_week(
        self, session: Session, team_id: int, week: int
    ) -> League | None:
        # get team
        team = session.exec(select(Team).where(Team.id == team_id)).first()
        if not team:
            return None

        # create team week
        team_week = TeamWeek(team_id=team_id, week=week)
        session.add(team_week)
        session.flush()

        # get league
        league = self.get_league(session, team.league_id)
        if not league:
            return None

        espn_league = self._espn.get_league(
            league_id=league.provider_league_id,
            year=league.year,
            espn_s2=league.espn_s2,
            swid=league.swid,
        )

        # get espn team
        espn_team = None
        for e_team in espn_league.teams:
            if e_team.id == team.provider_team_id:
                espn_team = e_team

        box_scores = espn_league.box_scores(week)

        box_score = next(
            (
                bs
                for bs in box_scores
                if bs.home_team == espn_team or bs.away_team == espn_team
            )
        )

        if box_score is None:
            return None

        is_away = box_score.away_team == team_id
        lineup = box_score.away_lineup if is_away else box_score.home_lineup

        opponent_projected = (
            box_score.home_projected if is_away else box_score.away_projected
        )

        all_player_ids = [player.playerId for player in espn_team]
        players_result = espn_league.player_info(playerId=all_player_ids)

        all_players_info = players_result if isinstance(players_result, list) else []
        player_info_lookup = {
            player.playerId: player.proTeam for player in all_players_info
        }

        team_week_player_list = []
        for player in lineup:
            team_week_player_list.append(
                TeamWeekPlayer(team_week_id=team_week.id, player_id=player.playerId)
            )

        return league


league_service = LeagueService(EspnClient())
