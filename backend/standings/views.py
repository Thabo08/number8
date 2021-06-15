from backend.standings.common import *
from backend.standings.common import config
from backend.standings.common import configure_logger
from backend.standings.common import logger_factory
from backend.standings.domain.config import ConfigProvider
from backend.standings.domain.leagues import Leagues
from backend.standings.domain.response.standings import MockStandingsSource
from backend.standings.domain.response.standings import Standings
from werkzeug.utils import import_string, cached_property

from markupsafe import escape
import requests

from backend.standings.domain.response.standings import standing_builder
from backend.standings.domain.storage.storage import Database
from backend.standings.domain.storage.storage import Key
from backend.standings.domain.storage.storage import MongoDB
from backend.standings.domain.storage.storage import RedisCache
from backend.standings.domain.storage.storage import Storage
from backend.standings.domain.storage.storage import database_provider

configure_logger("../log_config.yaml")
logger = logger_factory(__name__)

CONFIG = config('../config.json')
rapid_api_config = CONFIG["rapidapi"]
API_HOST = rapid_api_config[RAPID_API_HOST]
API_VERSION = rapid_api_config[RAPID_API_VESRION]
API_KEY = rapid_api_config[RAPID_API_KEY]
BASE_PATH = "standings"

storage_config = CONFIG["storage"]
storage_type = "real_database" if storage_config["real_database"] else "in_memory"


def get_storage():
    if storage_type == "in_memory":
        return Storage(database_provider(Database.is_in_memory(storage_type)))
    else:
        redis_cache = RedisCache(host=storage_config[REDIS_HOST], port=storage_config[REDIS_PORT])
        mongo_db = MongoDB(host=storage_config[MONGO_HOST], port=storage_config[MONGO_PORT],
                           username=storage_config[MONGO_USERNAME], password=storage_config[MONGO_PASSWORD])
        return Storage(database_provider(Database.is_in_memory(storage_type),
                                         redis_cache=redis_cache, mongo_db=mongo_db))


storage = get_storage()

# This is to enable testing without making a call to RapidAPI
MOCK_MODE = CONFIG["mock_mode"]
if CONFIG["mock_mode"]:
    mock = MockStandingsSource()


class LazyView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)


def get_league_standings(league, season):
    alias = league
    leagues = Leagues.get_instance(ConfigProvider('config/standings_config.json'))
    league = leagues.get_league(alias)  # TODO: Handle the LeagueNotFoundError thrown by this method
    league = escape(league.get_league_id())
    season = escape(season)

    key = Key(alias, season)
    in_cache, standings = storage.check_and_get(key)
    if in_cache:
        logger.info("Retrieving '%s' season standings for '%s' league from database", season, alias)
        return standings.as_json()

    return get_from_server(alias, key, league, season)


def get_from_server(alias, key, league, season):
    if MOCK_MODE:
        logger.info("Retrieving '%s' season standings for '%s' league from mock source", season, alias)
        standings = mock.get_standings(key)
    else:
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
