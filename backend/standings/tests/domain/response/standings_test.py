from unittest import TestCase
from unittest import mock
import json

from backend.standings.domain.response.standings import Record
from backend.standings.domain.response.standings import Records
from backend.standings.domain.response.standings import Standing
from backend.standings.domain.response.standings import Standings
from backend.standings.domain.response.standings import Team
from backend.standings.domain.response.standings import RecordTypeError
from backend.standings.domain.response.standings import standing_builder


class TeamTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(TeamTests, self).__init__(*args, **kwargs)
        self.team = Team(2, 'Inter', 'team.png', 'https://www.inter.it/en')

    def test_should_return_expected_team_values(self):
        self.assertEqual(2, self.team.get_id())
        self.assertEqual('Inter', self.team.get_name())
        self.assertEqual('team.png', self.team.get_logo())
        self.assertEqual('https://www.inter.it/en', self.team.get_homepage())

        self.assertEqual(self.team.__str__(), 'Inter')

    def test_team_equality(self):
        new_team = Team(2, 'Inter', 'team.png', 'https://www.inter.it/en')
        self.assertEqual(new_team, self.team)

        new_team = Team(20, 'Inter', 'team.png', 'https://www.inter.it/en')
        self.assertNotEqual(new_team, self.team)


class RecordTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(RecordTests, self).__init__(*args, **kwargs)
        self.record = Record("all", 20, 10, 5, 5, 20, 10)

    def test_should_return_expected_record_values(self):
        # played: int, wins: int, draws: int, loses: int, goals_for: int, goals_against: int

        self.assertEqual(20, self.record.get_played())
        self.assertEqual(10, self.record.get_wins())
        self.assertEqual(5, self.record.get_draws())
        self.assertEqual(5, self.record.get_loses())
        self.assertEqual(20, self.record.get_goals_for())
        self.assertEqual(10, self.record.get_goals_against())
        self.assertEqual(10, self.record.get_goal_diff())

    def test_record_equality(self):
        new_record = Record("all", 20, 10, 5, 5, 20, 10)
        self.assertEqual(self.record, new_record)

        new_record = Record("all", 20, 10, 5, 5, 20, 3)
        self.assertNotEqual(self.record, new_record)


class RecordsTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(RecordsTests, self).__init__(*args, **kwargs)
        self.records = Records()

    def test_should_return_record_if_added(self):
        record = Record("away", 20, 10, 5, 5, 20, 10)

        self.records.add_record(record)

        self.assertEqual(record, self.records.get_record("away"))

    def test_should_raise_error_if_unsupported_type_provided(self):
        record = Record("rubbish", 20, 10, 5, 5, 20, 10)
        self.assertRaises(RecordTypeError, self.records.add_record, record)

    def test_should_raise_error_if_unsupported_record_type_accessed(self):
        self.assertRaises(RecordTypeError, self.records.get_record, "rubbish")

    def test_should_raise_error_if_type_not_added(self):
        self.assertRaises(RecordTypeError, self.records.get_record, "home")


class StandingTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(StandingTests, self).__init__(*args, **kwargs)
        self.team = Team(2, 'Inter', 'https://media.api-sports.io/football/teams/505.png', 'https://www.inter.it/en')
        record = Record("all", 36, 27, 7, 2, 82, 31)
        self.records = Records()
        self.records.add_record(record)
        self.standing = Standing(rank=1, team=self.team, points=88, group="Serie A", form="WWWWD", records=self.records)

    def test_should_return_expected_standing_values(self):

        self.assertEqual(1, self.standing.get_rank())
        self.assertEqual(self.team, self.standing.get_team())
        self.assertEqual(88, self.standing.get_points())
        self.assertEqual("Serie A", self.standing.get_group())
        self.assertEqual("WWWWD", self.standing.get_form())
        self.assertEqual(36, self.standing.get_played())
        self.assertEqual(27, self.standing.get_wins())
        self.assertEqual(7, self.standing.get_draws())
        self.assertEqual(2, self.standing.get_loses())
        self.assertEqual(82, self.standing.get_goals_for())
        self.assertEqual(31, self.standing.get_goals_against())
        self.assertEqual(51, self.standing.get_goal_diff())

    def test_standing_build_properly(self):
        sample_standing_response = '{"rank": 1, "team": {"id": 505, "name": "Inter", "logo": ' \
                                   '"https://media.api-sports.io/football/teams/505.png"}, "points": 88, "goalsDiff": ' \
                                   '51, "group": "Serie A", "form": "WWWWD", "status": "same", "description": ' \
                                   '"Promotion - Champions League (Group Stage)", "all": {"played": 36, "win": 27, ' \
                                   '"draw": 7, "lose": 2, "goals": {"for": 82, "against": 31}}, "home": {"played": ' \
                                   '18, "win": 16, "draw": 1, "lose": 1, "goals": {"for": 48, "against": 17}}, ' \
                                   '"away": {"played": 18, "win": 11, "draw": 6, "lose": 1, "goals": {"for": 34, ' \
                                   '"against": 14}}, "update": "2021-05-15T00:00:00+00:00"} '
        standing = standing_builder(json.loads(sample_standing_response))
        self.assertIsNotNone(standing)

    def test_standing_equality(self):
        new_standing = Standing(rank=1, team=self.team, points=88, group="Serie A", form="WWWWD", records=self.records)
        self.assertEqual(self.standing, new_standing)

        new_standing = Standing(rank=3, team=self.team, points=90, group="Serie A", form="WWWWD", records=self.records)
        self.assertNotEqual(self.standing, new_standing)


class StandingsTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(StandingsTests, self).__init__(*args, **kwargs)

    def test_should_return_nothing_if_standing_not_added(self):
        standings = Standings()
        self.assertTrue(standings.is_empty())

    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_should_return_standings_if_standings_added(self, mock_standing):
        standings = Standings()
        standings.add(mock_standing)
        self.assertFalse(standings.is_empty())


