from flask import Flask
from markupsafe import escape
import json
import requests

app = Flask(__name__)


def _config(filename='../config.json'):
    with open(filename) as config_file:
        config = json.load(config_file)
    return config


CONFIG = _config()
API_HOST = CONFIG['rapidapi_host']
API_VERSION = CONFIG['rapidapi_version']
API_KEY = CONFIG['rapidapi_key']
BASE_PATH = "standings"


@app.route('/standings/<league>/<season>', methods=['GET'])
def get_league_standings(league, season):

    url = "https://{}/{}/{}".format(API_HOST, API_VERSION, BASE_PATH)

    league = escape(league)
    season = escape(season)

    querystring = {"season": season, "league": league}

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.text


