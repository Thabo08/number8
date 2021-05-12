from unittest import TestCase
from unittest import mock
from backend.standings.domain.leagues import League, Leagues


class LeagueTestCases(TestCase):
    def __init__(self, *args, **kwargs):
        super(LeagueTestCases, self).__init__(*args, **kwargs)
        self.league = League("England", "Premier League", 100, "league")

    def test_should_return_valid_league_name(self):
        self.assertEqual("Premier League", self.league.__str__(), "Name should be valid")

    def test_should_return_valid_league_id(self):
        self.assertEqual(100, self.league.get_league_id(), "League ID should be valid")


class LeaguesTestCases(TestCase):
    def __init__(self, *args, **kwargs):
        super(LeaguesTestCases, self).__init__(*args, **kwargs)

    @mock.patch('backend.standings.domain.config.ConfigProvider')
    def test_should_invoke_config_provider(self, mock_config_provider):
        Leagues(mock_config_provider)
        mock_config_provider.get_config_per_type.assert_called_with("leagues")

    def test_should_raise_value_error_when_alias_league_does_not_exist(self):
        pass


