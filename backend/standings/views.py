import requests
import sys
import datetime
from markupsafe import escape
from werkzeug.utils import cached_property
from werkzeug.utils import import_string

from backend.standings.common import *
from backend.standings.domain.config import ConfigProvider
from backend.standings.domain.leagues import LeagueException
from backend.standings.domain.leagues import Leagues
from backend.standings.domain.response.http_exceptions import ERROR_CODES
from backend.standings.domain.response.http_exceptions import client_error_response
from backend.standings.domain.response.http_exceptions import server_error_response
from backend.standings.domain.response.standings import MockStandingsSource
from backend.standings.domain.response.standings import Standings
from backend.standings.domain.response.standings import standing_builder
from backend.standings.domain.storage.storage import Database
from backend.standings.domain.storage.storage import Key
from backend.standings.domain.storage.storage import MongoDB
from backend.standings.domain.storage.storage import RedisCache
from backend.standings.domain.storage.storage import Storage
from backend.standings.domain.storage.storage import database_provider

configure_logger("../log_config.yaml")
logger = logger_factory(__name__)

CONFIG = app_config('../app_config.yaml')
rapid_api_config = CONFIG['rapidapi']
API_HOST = rapid_api_config['host']
API_VERSION = rapid_api_config['version']
API_KEY = rapid_api_config['key']
BASE_PATH = "standings"

storage_config = CONFIG['storage']
storage_type = "real_database" if storage_config['real_database'] else "in_memory"
not_container = sys.argv[1:][0] == 'not_container'


def get_storage():
    if storage_type == "in_memory":
        return Storage(database_provider(Database.is_in_memory(storage_type)))
    else:
        redis_config = storage_config['redis']
        redis_cache = RedisCache(host="localhost" if not_container else redis_config['host'],
                                 port=redis_config['port'], time_to_live_hours=redis_config['timeToLive'])
        mongo_config = storage_config['mongo']
        mongo_db = MongoDB(host="localhost" if not_container else mongo_config['host'],
                           port=mongo_config['port'], username=mongo_config['username'],
                           password=mongo_config['password'])
        return Storage(database_provider(Database.is_in_memory(storage_type),
                                         redis_cache=redis_cache, mongo_db=mongo_db))


storage = get_storage()

# This is to enable testing without making a call to RapidAPI
MOCK_MODE = CONFIG['mock_mode']
if CONFIG['mock_mode']:
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

    try:
        leagues = Leagues.get_instance(ConfigProvider(CONFIG['standings_config']))
    except FileNotFoundError as e:
        logger.error(e.__str__())
        return server_error_response(ERROR_CODES.get('server_error'))

    try:
        _seasons_validator(season, alias)
        league = leagues.get_league(alias)
    except LeagueException as e:
        logger.error(e.__str__())
        return client_error_response(e.__str__(), ERROR_CODES.get('bad_request'))

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
        response = _get_response(league, season, url)
        if response.status_code != 200:
            logger.error("Error reading from RapidApi. Status code: %s", response.status_code)
            return server_error_response(ERROR_CODES.get("server_error"))
        standings = Standings()
        standings_response = response.json()['response'][0]['league']['standings'][0]
        for standing_response in standings_response:
            standing = standing_builder(standing_response)
            standings.add(standing)
            logger.debug("Added standing: %s", standing)
    storage.store(key, standings)
    return standings.as_json()


def _get_response(league, season, url):
    querystring = {'season': season, 'league': league}
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }
    return requests.request("GET", url, headers=headers, params=querystring)


def _seasons_validator(season, alias):
    # todo: This validation probably belongs somewhere else
    season = int(season)
    start = 2010  # todo: make this configurable?
    end = datetime.datetime.now().year  # todo: Redirect if looking for standings of current year. This should look at
                                        # todo: whether that season exists
    if season < start or season > end:
        raise LeagueException("Invalid season '{}' for league alias '{}'".format(season, alias))
