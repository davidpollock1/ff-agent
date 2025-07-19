import pytest
from unittest.mock import MagicMock, patch
from dependency_builder import DependencyBuilder
from models import LeagueDep, MatchupDep


@pytest.fixture
def mock_league():
    league = MagicMock()
    league.settings.position_slot_counts = {
        "QB": 1,
        "RB": 2,
        "WR": 2,
        "TE": 1,
        "FLEX": 1,
        "IR": 1,
        "BE": 5,
    }
    league.settings.scoring_format = [
        {"abbr": "PY", "label": "Passing Yards", "id": 1, "points": 0.04}
    ]
    league.settings.matchup_periods = {1: [1, 2, 3]}
    league.settings.scoring_type = "PPR"
    league.settings.reg_season_count = 13
    league.settings.playoff_matchup_period_length = 2
    league.settings.playoff_seed_tie_rule = "points"
    league.teams = [MagicMock()]
    league.player_info.return_value = []
    return league


@pytest.fixture
def mock_box_score():
    box_score = MagicMock()
    box_score.away_team = 1
    box_score.home_team = 2
    box_score.away_lineup = []
    box_score.home_lineup = []
    box_score.away_projected = 100.0
    box_score.home_projected = 110.0
    box_score.is_playoff = False
    return box_score


@pytest.fixture
def mock_odds_api_client():
    client = MagicMock()
    client.get_events.return_value = MagicMock(events=[])
    client.get_team_totals_odds_for_event.return_value = MagicMock(bookmakers=[])
    return client


@patch("dependency_builder.SportsOddsApiClient")
def test_dependency_builder_basic(
    mock_odds_client_class, mock_league, mock_box_score, mock_odds_api_client
):
    mock_odds_client_class.return_value = mock_odds_api_client
    builder = DependencyBuilder(
        espn_league=mock_league, espn_box_score=mock_box_score, team_id=1
    )
    builder.with_league_dependency().with_matchup_dependency(
        week=1
    ).with_betting_odds_data()
    assert isinstance(builder._league_dep, LeagueDep)
    assert isinstance(builder._matchup_dep, MatchupDep)


@patch("dependency_builder.SportsOddsApiClient")
def test_dependency_builder_missing_odds(
    mock_odds_client_class, mock_league, mock_box_score, mock_odds_api_client
):
    mock_odds_api_client.get_events.return_value = None
    mock_odds_client_class.return_value = mock_odds_api_client
    builder = DependencyBuilder(
        espn_league=mock_league, espn_box_score=mock_box_score, team_id=1
    )
    builder.with_league_dependency().with_matchup_dependency(
        week=1
    ).with_betting_odds_data()
    assert builder._matchup_dep.my_team is None or isinstance(
        builder._matchup_dep, MatchupDep
    )
