from flask import Flask
from markupsafe import escape
import requests

from backend.standings.common import _config
from domain.leagues import Leagues, ConfigProvider

app = Flask(__name__)

CONFIG = _config('../config.json')
API_HOST = CONFIG['rapidapi_host']
API_VERSION = CONFIG['rapidapi_version']
API_KEY = CONFIG['rapidapi_key']
BASE_PATH = "standings"
leagues = Leagues(ConfigProvider('config/standings_config.json'))


@app.route('/standings/<league>/<season>', methods=['GET'])
def get_league_standings(league, season):
    url = "https://{}/{}/{}".format(API_HOST, API_VERSION, BASE_PATH)

    league = leagues.get_league(league)
    print("Retrieving standings for league: {}".format(league))
    league = escape(league.get_league_id())
    season = escape(season)

    querystring = {"season": season, "league": league}

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.text


if __name__ == '__main__':
    app.run(debug=True)
