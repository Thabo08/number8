from unittest import TestCase
import os

from backend.standings.domain.config import ConfigProvider
from backend.standings.domain.leagues import League, Leagues
from backend.standings.domain.leagues import LeagueException


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
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_config = os.path.abspath(os.path.join(test_dir, '../test_files/test_config.json'))
        self.config_provider = ConfigProvider(test_config)
        self.leagues = Leagues.get_instance(self.config_provider)

    def test_should_invoke_config_provider(self):
        self.assertIsNotNone(self.config_provider.get_config_per_type("leagues"))

    def test_should_return_valid_league_when_alias_exists(self):
        self.assertIsNotNone(self.leagues.get_league("epl"), "League with alias {} should exist".format("epl"))

    def test_should_raise_value_error_when_alias_league_does_not_exist(self):
        self.assertRaises(LeagueException, self.leagues.get_league, "rubbish")


