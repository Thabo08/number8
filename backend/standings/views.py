from backend.standings.common import config
from backend.standings.common import logger_factory
from backend.standings.domain.config import ConfigProvider
from backend.standings.domain.leagues import Leagues
from backend.standings.domain.response.standings import Standings
from werkzeug.utils import import_string, cached_property


from markupsafe import escape
import requests

from backend.standings.domain.response.standings import standing_builder
from backend.standings.domain.storage.storage import Storage

leagues = Leagues(ConfigProvider('config/standings_config.json'))
logger = logger_factory(__name__)

CONFIG = config('../config.json')
API_HOST = CONFIG['rapidapi_host']
API_VERSION = CONFIG['rapidapi_version']
API_KEY = CONFIG['rapidapi_key']
BASE_PATH = "standings"

storage = Storage('in_memory')


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

    league = leagues.get_league(league)  # TODO: Handle the LeagueNotFoundError thrown by this method
    league = escape(league.get_league_id())
    season = escape(season)

    key = storage_key(league, season)
    if storage.contains_standings(key):
        logger.info("Retrieving '%s' season standings for '%s' league from database", season, league)
        standings = storage.get(key)
        return standings.as_json()

    url = "https://{}/{}/{}".format(API_HOST, API_VERSION, BASE_PATH)
    logger.info("Retrieving '%s' season standings for '%s' league from '%s'", season, league, url)

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
