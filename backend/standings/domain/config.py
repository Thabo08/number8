
"""This module is responsible for supplying config to the caller """
from backend.standings.common import _config


class ConfigProvider:
    """This class loads the config and makes it available to the callers"""
    def __init__(self, config_file: str):
        self.config = _config(config_file)

    def get_config_per_type(self, config_type: str):
        """This method gets config per type from the loaded config

            :param config_type The type of the config, e.g, "leagues"
            :return Config for the type, which is a json dictionary
            :raise ValueError if config for the type does not exist
        """
        config_for_type = self.config.get(config_type)
        if config_for_type is None:
            raise ValueError("Config for type {} does not exist".format(config_type))
        return config_for_type
