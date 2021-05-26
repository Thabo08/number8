from backend.standings.common import logger_factory
from backend.standings.domain.response.standings import Standings

Storage_Types = ['in_memory', 'database']


class Storage:
    """ Interface that makes it known to the caller whether the required standings are in the storage or not """
    def __init__(self, storage_type):
        if storage_type == 'in_memory':
            self.database = _InMemory()
        else:
            raise ValueError('Unsupported storage type: ', storage_type)

    def contains_standings(self, key):
        return self.database.contains_key(key)

    def get(self, key):
        return self.database.get(key)

    def store(self, key, standings: Standings):
        self.database.store(key, standings)


class _InMemory:
    def __init__(self):
        self.logger = logger_factory(_InMemory.__name__)
        self.database = {}

    def store(self, key, standings):
        self.logger.info("Storing standings for %s", key)
        self.database[key] = standings

    def contains_key(self, key):
        exists = self.database.get(key) is not None
        message = "Standings for key {} exist".format(key if exists else key + " does not ")
        self.logger.info(message)
        return exists

    def get(self, key):
        return self.database.get(key)
