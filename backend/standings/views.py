from backend.standings.common import config
from backend.standings.common import logger_factory
from backend.standings.domain.config import ConfigProvider
from backend.standings.domain.leagues import Leagues
from backend.standings.domain.response.standings import Standings
from werkzeug.utils import import_string, cached_property


from markupsafe import escape
import requests

from backend.standings.domain.response.standings import standing_builder
from backend.standings.domain.storage.storage import Database
from backend.standings.domain.storage.storage import Storage
from backend.standings.domain.storage.storage import database_provider

leagues = Leagues(ConfigProvider('config/standings_config.json'))
logger = logger_factory(__name__)

CONFIG = config('../config.json')
API_HOST = CONFIG['rapidapi_host']
API_VERSION = CONFIG['rapidapi_version']
API_KEY = CONFIG['rapidapi_key']
BASE_PATH = "standings"

storage = Storage(database_provider(Database.is_in_memory("in_memory")))


class LazyView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)


def storage_key(league, season):
    return "{0}_{1}".format(league, season)


def get_league_standings(league, season):

    alias = league
    league = leagues.get_league(alias)  # TODO: Handle the LeagueNotFoundError thrown by this method
    league = escape(league.get_league_id())
    season = escape(season)

    key = storage_key(alias, season)
    if storage.contains_standings(key):
        return get_from_storage(alias, key, season)

    return get_from_server(alias, key, league, season)


def get_from_server(alias, key, league, season):
    url = "https://{}/{}/{}".format(API_HOST, API_VERSION, BASE_PATH)
    logger.info("Retrieving '%s' season standings for '%s' league from '%s'", season, alias, url)
    querystring = {"season": season, "league": league}
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    standings = Standings()
    standings_response = response.json()['response'][0]['league']['standings'][0]
    for standing_response in standings_response:
        standing = standing_builder(standing_response)
        standings.add(standing)
        logger.debug("Added standing: %s", standing)
    storage.store(key, standings)
    return standings.as_json()


def get_from_storage(alias, key, season):
    logger.info("Retrieving '%s' season standings for '%s' league from database", season, alias)
    standings = storage.get(key)
    return standings.as_json()
