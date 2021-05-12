import json
from config import ConfigProvider


class League:
    """ This type holds the details of a league """
    def __init__(self, country: str, name: str, league_id: int, league_type="league"):
        self.country = country
        self.name = name
        self.league_id = league_id
        self.league_type = league_type


LEAGUES = {"39": "Premier League",
           "40": "Championship",
           "140": "Primera Division",
           "141": "Segunda Division",
           "135": "Serie A",
           "136": "Serie B",
           "61": "Ligue 1",
           "62": "Ligue 2",
           "78": "Bundesliga 1",
           "79": "Bundesliga 2"}


def _load_leagues():
    return {"epl": League("England", "Premier League", 39), "championship": League("England", "Championship", 40),
            "laliga": League("Spain", "Primera Division", 140),
            "laliga2": League("Spain", "Segunda Division", 141),
            "seriea": League("Italy", "Serie A", 135), "serieb": League("Italy", "Serie B", 136),
            "ligue1": League("France", "Ligue 1", 61), "ligue2": League("France", "Ligue 2", 62),
            "bundesliga": League("Germany", "Bundesliga 1", 78),
            "bundesliga2": League("Germany", "Bundesliga 2", 79)}


SUPPORTED_COUNTRIES = ["England", "Spain", "Italy", "France", "Germany"]
SUPPORTED_LEAGUES = ["Premier League", "Championship", "Primera Division", "Segunda Division",
                     "Serie A", "Serie B", "Ligue 1", "Ligue 2", "Bundesliga 1", "Bundesliga 2"]


def _validate(country: str, league: str):
    def validate(to_validate, singular, plural, supported):
        if to_validate not in supported:
            error = "{} is not a supported {}. Supported {} are: ".format(to_validate, singular, plural)
            for c in supported:
                error += "{}, ".format(c)
            raise ValueError(error)

    validate(country, "country", "countries", SUPPORTED_COUNTRIES)
    validate(league, "league", "leagues", SUPPORTED_LEAGUES)


class Leagues:
    def __init__(self):
        self.leagues = _load_leagues()

    def get_league(self, league_alias):
        return self.leagues[league_alias].league_id


def _config(filename='../config/standings_config.json'):
    with open(filename) as config_file:
        config = json.load(config_file)
    return config


def _load_leagues_from_config(config_provider: ConfigProvider, config_type):
    leagues = config_provider.get_config_per_type(config_type)
    countries = leagues.keys()
    for country in countries:
        aliases = country.keys()
        for alias in aliases:
            id = alias["id"]
            name = alias["name"]
            type_ = alias["type"]
            print(id, name, type_)


class Leagues2:
    def __init__(self, config_provider: ConfigProvider):
        self.leagues = _load_leagues_from_config(config_provider, "leagues")


if __name__ == '__main__':
    # c = _config()
    # print(c["leagues"])
    config_provider = ConfigProvider('../config/standings_config.json')
    _load_leagues_from_config(config_provider, "leagues")
