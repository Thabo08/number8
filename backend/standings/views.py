from backend.standings.common import config
from backend.standings.common import logger_factory
from backend.standings.domain.config import ConfigProvider
from backend.standings.domain.leagues import Leagues
from backend.standings.domain.response.standings import Standings
from werkzeug.utils import import_string, cached_property


from markupsafe import escape
import requests

from backend.standings.domain.response.standings import standing_builder

leagues = Leagues(ConfigProvider('config/standings_config.json'))
logger = logger_factory(__name__)

CONFIG = config('../config.json')
API_HOST = CONFIG['rapidapi_host']
API_VERSION = CONFIG['rapidapi_version']
API_KEY = CONFIG['rapidapi_key']
BASE_PATH = "standings"


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
    url = "https://{}/{}/{}".format(API_HOST, API_VERSION, BASE_PATH)

    league = leagues.get_league(league)  # TODO: Handle the LeagueNotFoundError thrown by this method
    logger.info("Retrieving '%s' season standings for '%s' league from '%s'", season, league, url)
    league = escape(league.get_league_id())
    season = escape(season)

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
    return standings.as_json()
