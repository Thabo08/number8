import subprocess
import sys
from flask import Flask

from backend.standings.common import configure_logger
from backend.standings.common import logger_factory
from backend.standings.views import LazyView

app = Flask(__name__)

configure_logger("../log_config.yaml")
logger = logger_factory(__name__)


if __name__ == '__main__':
    if '--unittest' in sys.argv:
        subprocess.call([sys.executable, '-m', 'unittest', 'discover'])
    logger.info("Starting Standings service")
    app = Flask(__name__)
    app.add_url_rule('/standings/<league>/<season>',
                     view_func=LazyView('views.get_league_standings'))
    app.run(debug=True)
