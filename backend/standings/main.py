import sys
from flask import Flask

from backend.standings.common import configure_logger
from backend.standings.common import logger_factory
from backend.standings.views import LazyView

app = Flask(__name__)

configure_logger("../log_config.yaml")
logger = logger_factory(__name__)

logger.info("Started Standings service")

app.add_url_rule('/standings/<league>/<season>', view_func=LazyView('views.get_league_standings'))

app.add_url_rule('/', view_func=LazyView('views.get_hello'))


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 0:
        not_container = args[0] == 'not_container'

        if not_container:
            app.run(debug=True, port=5000)
