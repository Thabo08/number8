"""This file holds common functionality required in other files and classes """

from os import path
import json


def config(config_file):
    if not path.exists(config_file):
        raise FileNotFoundError("{} does not exist".format(config_file))
    with open(config_file) as config_file:
        config = json.load(config_file)
    return config
