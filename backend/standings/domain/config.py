
"""This module is responsible for supplying config to the caller """
from backend.standings.common import config
from backend.standings.common import logger_factory


class ConfigProvider:
    """This class loads the config and makes it available to the callers"""
    def __init__(self, config_file: str):
        self.logger = logger_factory(ConfigProvider.__name__)
        try:
            self.config = config(config_file)
        except FileNotFoundError as e:
            self.logger.error(e.__str__())
            raise

    def get_config_per_type(self, config_type: str):
        """This method gets config per type from the loaded config

            :param config_type The type of the config, e.g, "leagues"
            :return Config for the type, which is a json dictionary
            :raises ValueError if config for the type does not exist
        """
        config_for_type = self.config.get(config_type)
        if config_for_type is None:
            self.logger.error("Config for type %s does not exist", config_type)
            raise ValueError("Config for type {} does not exist".format(config_type))
        self.logger.debug("Returning config for type %s", config_type)
        return config_for_type
