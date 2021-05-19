import logging
import logging.config
import yaml

with open('log_config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def logger_factory(name):
    return logging.getLogger(name)

