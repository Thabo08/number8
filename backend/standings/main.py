import sys

from flask import Flask
from markupsafe import escape
import requests
import subprocess

from backend.standings.common import config
from backend.standings.domain.response.standings import Standings
from backend.standings.domain.response.standings import standing_builder
from backend.standings.loggers import logger_factory
from domain.leagues import Leagues, ConfigProvider

app = Flask(__name__)

leagues = Leagues(ConfigProvider('config/standings_config.json'))
logger = logger_factory(__name__)


@app.route('/standings/<league>/<season>', methods=['GET'])
def get_league_standings(league, season):
    url = "https://{}/{}/{}".format(API_HOST, API_VERSION, BASE_PATH)

    league = leagues.get_league(league)  # TODO: Handle the LeagueNotFoundError thrown by this method
    logger.info("Retrieving standings for '%s' league from %s", league, url)
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


if __name__ == '__main__':
    if '--unittest' in sys.argv:
        subprocess.call([sys.executable, '-m', 'unittest', 'discover'])
    logger.info("Starting Standings service")
    global CONFIG
    global API_HOST
    global API_VERSION
    global API_KEY
    global BASE_PATH
    CONFIG = config('../config.json')
    API_HOST = CONFIG['rapidapi_host']
    API_VERSION = CONFIG['rapidapi_version']
    API_KEY = CONFIG['rapidapi_key']
    BASE_PATH = "standings"
    app.run(debug=True)
