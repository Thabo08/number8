""" This module holds the information about league standings """

#{'rank': 1, 'team': {'id': 505, 'name': 'Inter', 'logo': 'https://media.api-sports.io/football/teams/505.png'}, 'points': 88, 'goalsDiff': 51, 'group': 'Serie A', 'form': 'WWWWD', 'status': 'same', 'description': 'Promotion - Champions League (Group Stage)', 'all': {'played': 36, 'win': 27, 'draw': 7, 'lose': 2, 'goals': {'for': 82, 'against': 31}}, 'home': {'played': 18, 'win': 16, 'draw': 1, 'lose': 1, 'goals': {'for': 48, 'against': 17}}, 'away': {'played': 18, 'win': 11, 'draw': 6, 'lose': 1, 'goals': {'for': 34, 'against': 14}}, 'update': '2021-05-15T00:00:00+00:00'}
# standings = response.json()['response'][0]['league']['standings'][0]
# for s in standings:
#     print(s)

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


# 'all': {'played': 36, 'win': 27, 'draw': 7, 'lose': 2, 'goals': {'for': 82, 'against': 31}}
class Record:
    """ Information about team's record in games """
    def __init__(self, played: int, wins: int, draws: int, loses: int, goals_for: int, goals_against: int):
        self.played = played
        self.wins = wins
        self.draws = draws
        self.loses = loses
        self.goals_for = goals_for
        self.goals_against = goals_against
        self.goal_diff = self.goals_for - self.goals_against

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

    def add_record(self, type_: str, record: Record):
        self.validate_type_support(type_)
        self.records[type_] = record

    def get(self, type_="all"):
        self.validate_type_support(type_)
        record = self.records.get(type_)
        if record is None:
            raise RecordTypeError("{} record wanted but never added".format(type_))
        return record

    def validate_type_support(self, type_):
        if not self.is_supported(type_):
            raise RecordTypeError("{} record is not supported".format(type_))


class RecordTypeError(KeyError):
    def __init__(self, message):
        super(RecordTypeError, self).__init__(message)


class Standing:
    """ All information about a standing """
    def __init__(self, rank: int, team: Team, points: int, group: str, form: str):
        self.rank = rank
        self.team = team
        self.points = points
        self.group = group
        self.form = form
