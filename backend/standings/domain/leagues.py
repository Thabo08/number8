"""This module is responsible for supplying config to the caller """
from backend.standings.common import logger_factory
from backend.standings.domain.config import ConfigProvider

ID = "id"
NAME = "name"
TYPE = "type"


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
    """This holds a dictionary/map of :func:`League` objects. Loaded from config file, a :func:`League` object can
        retrieved by passing the league alias to the :func:`League.get_league` method.
    """
    def __init__(self, config_provider: ConfigProvider):
        self.logger = logger_factory(Leagues.__name__)
        self.leagues = _load_leagues_from_config(config_provider, self.logger)

    def get_league(self, alias):
        """ Get :func:`League` object associated with an alias

            :param alias An alias associated with a league. Eg, 'Premier League' is associated with 'epl' alias
            :returns :func:`League` object
            :raises LeagueNotFoundError if no League with alias exists
        """
        assert alias is not None, "Alias cannot be None"
        league = self.leagues.get(alias)
        if league is None:
            self.logger.error("No league with alias: %s", alias)
            raise LeagueNotFoundError("No league with alias: {}".format(alias))
        return league


def _load_leagues_from_config(config_provider: ConfigProvider, logger, config_type="leagues"):
    leagues = config_provider.get_config_per_type(config_type)
    countries = leagues.keys()
    loaded_leagues = {}
    for country in countries:
        country_leagues = dict(leagues[country])
        aliases = country_leagues.keys()
        for alias in aliases:
            league = country_leagues[alias]
            id_ = league[ID]
            name = league[NAME]
            type_ = league[TYPE]
            league_object = League(country, name, id_, type_)
            loaded_leagues[alias] = league_object
            logger.debug("Loaded league: %s", league_object)
    return loaded_leagues


class LeagueNotFoundError(Exception):
    def __init__(self, message):
        super(LeagueNotFoundError, self).__init__(message)

