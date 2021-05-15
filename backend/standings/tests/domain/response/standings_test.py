from unittest import TestCase

from backend.standings.domain.response.standings import Record
from backend.standings.domain.response.standings import Team


class TeamTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(TeamTests, self).__init__(*args, **kwargs)
        self.team = Team(2, 'Inter', 'team.png', 'www.google.com')

    def test_should_return_expected_team_values(self):
        self.assertEqual(2, self.team.get_id())
        self.assertEqual('Inter', self.team.get_name())
        self.assertEqual('team.png', self.team.get_logo())
        self.assertEqual('www.google.com', self.team.get_homepage())

        self.assertEqual(self.team.__str__(), 'Inter')


class RecordTests(TestCase):
    def __init__(self, *args, **kwargs):
        super(RecordTests, self).__init__(*args, **kwargs)

    def test_should_return_expected_record_values(self):
        # played: int, wins: int, draws: int, loses: int, goals_for: int, goals_against: int
        self.record = Record(20, 10, 5, 5, 20, 10)

        self.assertEqual(20, self.record.get_played())
        self.assertEqual(10, self.record.get_wins())
        self.assertEqual(5, self.record.get_draws())
        self.assertEqual(5, self.record.get_loses())
        self.assertEqual(20, self.record.get_goals_for())
        self.assertEqual(10, self.record.get_goals_against())
        self.assertEqual(10, self.record.get_goal_diff())
