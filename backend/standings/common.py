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
    logger = logging.getLogger(name)
    logger.disabled = False  # In case the logger is disabled
    return logger


def configure_logger(config_file):
    with open(config_file, 'r') as f:
        logger_config = yaml.safe_load(f.read())
        logging.config.dictConfig(logger_config)


def equality_tester(self_, clazz, other):
    if isinstance(other, clazz):
        for var in vars(self_):
            var_of_self = getattr(self_, var)
            var_of_other = getattr(other, var)

            if var_of_self != var_of_other:
                return False
        return True
    return False

