""" This module holds the information about league standings """

# {'rank': 1, 'team': {'id': 505, 'name': 'Inter', 'logo': 'https://media.api-sports.io/football/teams/505.png'},
# 'points': 88, 'goalsDiff': 51, 'group': 'Serie A', 'form': 'WWWWD', 'status': 'same', 'description': 'Promotion -
# Champions League (Group Stage)', 'all': {'played': 36, 'win': 27, 'draw': 7, 'lose': 2, 'goals': {'for': 82,
# 'against': 31}}, 'home': {'played': 18, 'win': 16, 'draw': 1, 'lose': 1, 'goals': {'for': 48, 'against': 17}},
# 'away': {'played': 18, 'win': 11, 'draw': 6, 'lose': 1, 'goals': {'for': 34, 'against': 14}}, 'update':
# '2021-05-15T00:00:00+00:00'}

import json


class Team:
    """ All the information about a team """

    def __init__(self, id_: int, name: str, logo: str, homepage=""):
        self.id_ = id_
        self.name = name
        self.logo = logo
        self.homepage = homepage

    def get_id(self):
        return self.id_

    def get_name(self):
        return self.name

    def get_logo(self):
        return self.logo

    def get_homepage(self):
        return self.homepage

    def __str__(self):
        return self.name


class Goals:
    def __init__(self, goals_for, goals_against):
        self.goals_for = goals_for
        self.goals_against = goals_against

    def get_goals_for(self):
        return self.goals_for

    def get_goals_against(self):
        return self.goals_against


class Record:
    """ Information about team's record in games """

    def __init__(self, type_: str, played: int, wins: int, draws: int, loses: int, goals_for: int, goals_against: int):
        self.type_ = type_
        self.played = played
        self.wins = wins
        self.draws = draws
        self.loses = loses
        self.goals_for = goals_for
        self.goals_against = goals_against
        self.goal_diff = self.goals_for - self.goals_against

    def get_type(self):
        return self.type_

    def get_played(self):
        return self.played

    def get_wins(self):
        return self.wins

    def get_draws(self):
        return self.draws

    def get_loses(self):
        return self.loses

    def get_goals_for(self):
        return self.goals_for

    def get_goals_against(self):
        return self.goals_against

    def get_goal_diff(self):
        return self.goal_diff


class Records:
    def __init__(self, supported_types=None):
        if supported_types is None:
            supported_types = ["all", "home", "away"]
        self.is_supported = lambda type_: type_ in supported_types
        self.records = {}

    def add_record(self, record: Record):
        type_ = record.get_type()
        self.validate_type_support(type_)
        self.records[type_] = record

    def get_record(self, type_="all"):
        self.validate_type_support(type_)
        record = self.records.get(type_)
        if record is None:
            raise RecordTypeError("'{}' record wanted but never added".format(type_))
        return record

    def validate_type_support(self, type_):
        if not self.is_supported(type_):
            raise RecordTypeError("'{}' record is not supported".format(type_))


class RecordTypeError(KeyError):
    def __init__(self, message):
        super(RecordTypeError, self).__init__(message)


class Standing:
    """ All information about a standing """

    def __init__(self, rank: int, team: Team, points: int, group: str, form: str, records: Records):
        self.rank = rank
        self.team = team
        self.points = points
        self.group = group
        self.form = form
        self.record = records.get_record()

    def get_played(self):
        return self.record.get_played()

    def get_wins(self):
        return self.record.get_wins()

    def get_draws(self):
        return self.record.get_draws()

    def get_loses(self):
        return self.record.get_loses()

    def get_goals_for(self):
        return self.record.get_goals_for()

    def get_goals_against(self):
        return self.record.get_goals_against()

    def get_goal_diff(self):
        return self.record.get_goal_diff()

    def get_rank(self):
        return self.rank

    def get_team(self):
        return self.team

    def get_points(self):
        return self.points

    def get_group(self):
        return self.group

    def get_form(self):
        return self.form

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Standings:
    """ This is a collection of all standings for a league at a given time"""

    def __init__(self):
        self.standings = {}

    def add(self, standing: Standing):
        assert standing is not None
        rank = standing.get_rank()
        self.standings[rank] = standing

    def get_all(self):
        return self.standings

    def is_empty(self):
        return len(self.standings) == 0

    def as_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)


def standing_builder(standing_response):
    """ Builds a standing from json text

        :param standing_response: Standing response in json format
        :return Standing
     """
    rank = standing_response['rank']
    team = _team_builder(standing_response['team'])
    points = standing_response['points']
    group = standing_response['group']
    form = standing_response['form']
    record = _record_builder(standing_response['all'])
    records = Records()
    records.add_record(record)

    return Standing(rank=rank, team=team, points=points, group=group, form=form, records=records)


def _team_builder(team_response):
    return Team(id_=team_response['id'], name=team_response['name'], logo=team_response['logo'])


def _record_builder(record_response):
    played = record_response['played']
    wins = record_response['win']
    draws = record_response['draw']
    loses = record_response['lose']
    goals = _goals_builder(record_response['goals'])
    goals_for = goals.get_goals_for()
    goals_against = goals.get_goals_against()

    return Record(type_="all", played=played, wins=wins, draws=draws, loses=loses,
                  goals_for=goals_for, goals_against=goals_against)


def _goals_builder(goals_response):
    goals_for = goals_response['for']
    goals_against = goals_response['against']

    return Goals(goals_for=goals_for, goals_against=goals_against)
