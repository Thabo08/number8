"""This module is responsible for supplying config to the caller """

from backend.standings.domain.config import ConfigProvider


class League:
    """ This type holds the details of a league """
    def __init__(self, country: str, name: str, league_id: int, league_type="league"):
        self.country = country
        self.name = name
        self.league_id = league_id
        self.league_type = league_type

    def get_league_id(self):
        return self.league_id

    def __str__(self):
        return self.name


class Leagues:
    def __init__(self, config_provider: ConfigProvider):
        self.leagues = _load_leagues_from_config(config_provider, "leagues")

    def get_league(self, alias):
        assert alias is not None, "Alias cannot be None"
        league = self.leagues.get(alias)
        if league is None:
            raise ValueError("No league with alias: {}".format(alias))
        return league


def _load_leagues_from_config(config_provider: ConfigProvider, config_type):
    leagues = config_provider.get_config_per_type(config_type)
    countries = leagues.keys()
    loaded_leagues = {}
    for country in countries:
        country_leagues = dict(leagues[country])
        aliases = country_leagues.keys()
        for alias in aliases:
            league = country_leagues[alias]
            id_ = league["id"]
            name = league["name"]
            type_ = league["type"]
            league_object = League(country, name, id_, type_)
            loaded_leagues[alias] = league_object
            print("Loaded league: {}".format(league_object))
    return loaded_leagues

