from unittest import TestCase
from unittest import mock

from backend.standings.domain.response.standings import Record
from backend.standings.domain.response.standings import Records
from backend.standings.domain.response.standings import Standing
from backend.standings.domain.response.standings import Standings
from backend.standings.domain.response.standings import Team
from backend.standings.domain.response.standings import RecordTypeError


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


class RecordTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(RecordTests, self).__init__(*args, **kwargs)

    def test_should_return_expected_record_values(self):
        # played: int, wins: int, draws: int, loses: int, goals_for: int, goals_against: int
        self.record = Record("all", 20, 10, 5, 5, 20, 10)

        self.assertEqual(20, self.record.get_played())
        self.assertEqual(10, self.record.get_wins())
        self.assertEqual(5, self.record.get_draws())
        self.assertEqual(5, self.record.get_loses())
        self.assertEqual(20, self.record.get_goals_for())
        self.assertEqual(10, self.record.get_goals_against())
        self.assertEqual(10, self.record.get_goal_diff())


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

    def test_should_return_expected_standing_values(self):
        team = Team(2, 'Inter', 'https://media.api-sports.io/football/teams/505.png', 'https://www.inter.it/en')
        record = Record("all", 36, 27, 7, 2, 82, 31)
        records = Records()
        records.add_record(record)
        standing = Standing(rank=1, team=team, points=88, group="Serie A", form="WWWWD", records=records)

        self.assertEqual(1, standing.get_rank())
        self.assertEqual(team, standing.get_team())
        self.assertEqual(88, standing.get_points())
        self.assertEqual("Serie A", standing.get_group())
        self.assertEqual("WWWWD", standing.get_form())
        self.assertEqual(36, standing.get_played())
        self.assertEqual(27, standing.get_wins())
        self.assertEqual(7, standing.get_draws())
        self.assertEqual(2, standing.get_loses())
        self.assertEqual(82, standing.get_goals_for())
        self.assertEqual(31, standing.get_goals_against())
        self.assertEqual(51, standing.get_goal_diff())


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
