"""This file holds common functionality required in other files and classes """

import json
import yaml
import logging
import logging.config
from os import path


def config(config_file):
    if not path.exists(config_file):
        raise FileNotFoundError("{} does not exist".format(config_file))
    with open(config_file) as config_file:
        config = json.load(config_file)
    return config


def logger_factory(name):
    return logging.getLogger(name)


def configure_logger(config_file):
    with open(config_file, 'r') as f:
        logger_config = yaml.safe_load(f.read())
        logging.config.dictConfig(logger_config)
