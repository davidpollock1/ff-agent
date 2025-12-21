from datetime import datetime
from sqlmodel import Session, select
from app.models.models import League, Team, TeamWeek, TeamWeekPlayer, Player, PlayerWeek
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
        provider_league_id: str,
        name: str,
        year: int,
        espn_s2: str,
        swid: str,
        user: User,
    ) -> League:
        league = League(
            name=name,
            provider_league_id=provider_league_id,
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
        provider_league_id: str,
        name: str,
        year: int,
        espn_s2: str,
        swid: str,
        provider_team_id: int,
        user: User,
    ) -> tuple[League, Team]:
        league = self.create_league(
            session=session,
            provider_league_id=provider_league_id,
            name=name,
            year=year,
            espn_s2=espn_s2,
            swid=swid,
            user=user,
        )
        session.flush()

        espn_league = self._espn.get_league(
            league_id=league.provider_league_id,
            year=league.year if league.year is not None else datetime.now().year,
            espn_s2=league.espn_s2,
            swid=league.swid,
        )

        espn_team = None
        for e_team in espn_league.teams:
            if e_team.team_id == provider_team_id:
                espn_team = e_team

        if espn_team is None:
            return League(), Team()

        team = Team(
            league_id=league.id,
            user_id=user.id,
            name=espn_team.team_name,
            owner=espn_team.owners[0].get("displayName"),
            provider_team_id=espn_team.team_id,
        )

        session.add(team)
        session.commit()
        session.refresh(league)

        return league, team

    def get_league(self, session: Session, id: int) -> League | None:
        return session.exec(select(League).where(League.id == id)).first()

    # TODO: Refactor
    def sync_team_week(self, session: Session, team_id: int, week: int) -> bool:
        # get team
        team = session.exec(select(Team).where(Team.id == team_id)).first()
        if not team:
            return False

        # create team week
        team_week = session.exec(
            select(TeamWeek)
            .where(TeamWeek.team_id == team_id)
            .where(TeamWeek.week == week)
        ).first()

        if team_week is None:
            team_week = TeamWeek(team_id=team_id, week=week)
            session.add(team_week)
            session.flush()

        # get league
        league = self.get_league(session, team.league_id)
        if not league:
            return False

        espn_league = self._espn.get_league(
            league_id=league.provider_league_id,
            year=league.year if league.year is not None else datetime.now().year,
            espn_s2=league.espn_s2,
            swid=league.swid,
        )

        # get espn team
        espn_team = None
        for e_team in espn_league.teams:
            if e_team.team_id == int(team.provider_team_id):
                espn_team = e_team
                break

        if espn_team is None:
            return False

        box_scores = espn_league.box_scores(week)

        box_score = next(
            (
                bs
                for bs in box_scores
                if bs.home_team.team_id == int(team.provider_team_id)
                or bs.away_team.team_id == int(team.provider_team_id)
            ),
            None,
        )

        if box_score is None:
            return False

        is_away = box_score.away_team.team_id == int(team.provider_team_id)
        lineup = box_score.away_lineup if is_away else box_score.home_lineup

        # opponent_projected = (
        #     box_score.home_projected if is_away else box_score.away_projected
        # )

        all_player_ids = [player.playerId for player in lineup]
        players_result = espn_league.player_info(playerId=all_player_ids)

        all_players_info = players_result if isinstance(players_result, list) else []
        player_info_lookup = {
            player.playerId: player.proTeam for player in all_players_info
        }

        for player in lineup:
            new_player = Player(
                provider_player_id=player.playerId,
                name=player.name,
                position=player.position,
                professional_team=player_info_lookup.get(player.playerId, ""),
            )

            player_week = PlayerWeek(
                professional_team_opponent=player.pro_opponent,
                projected_points=player.projected_points,
                player=new_player,
            )

            team_week_player = TeamWeekPlayer(
                team_week_id=team_week.id, player_week=player_week
            )

            session.add(new_player)
            session.add(player_week)
            session.add(team_week_player)

        session.commit()
        return True

    def upsert_players(self, session: Session, players: list[Player]) -> None:
        if not players:
            return

        stmt = insert(Player).values(
            [player.model_dump(exclude_unset=True) for player in players]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["provider_player_id"],
            set_={
                "name": stmt.excluded.name,
                "position": stmt.excluded.position,
                "professional_team": stmt.excluded.professional_team,
            },
        )

        session.execute(stmt)
        session.commit()

    def upsert_playerweeks(
        self, session: Session, playerweeks: list[PlayerWeek]
    ) -> None:
        if not playerweeks:
            return

        stmt = insert(PlayerWeek).values(
            [pw.model_dump(exclude_unset=True) for pw in playerweeks]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["provider_player_id", "event_id"],
            set_={
                "name": stmt.excluded.name,
                "position": stmt.excluded.position,
                "professional_team": stmt.excluded.professional_team,
                "professional_team_opponent": stmt.excluded.professional_team_opponent,
                "projected_points": stmt.excluded.projected_points,
            },
        )

        session.execute(stmt)
        session.commit()


league_service = LeagueService(EspnClient())
