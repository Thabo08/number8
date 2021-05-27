
from backend.standings.common import logger_factory
from backend.standings.domain.response.standings import Standings


class Database:
    def __init__(self):
        self.logger = logger_factory(Database.__name__)
        self.logger.info("Using {} database", self)

    def store(self, key: str, standings: Standings):
        raise NotImplementedError("Method not implemented")

    def contains_key(self, key: str):
        raise NotImplementedError("Method not implemented")

    def get(self, key):
        raise NotImplementedError("Method not implemented")

    def __str__(self):
        raise NotImplementedError("Method not implemented")

    @staticmethod
    def is_in_memory(database_type):
        is_supported = database_type == "in_memory" or database_type == "real_database"
        if not is_supported:
            raise ValueError("Unknown database type: {}".format(database_type))
        return database_type == "in_memory"


class _InMemoryDatabase(Database):
    def __init__(self):
        super().__init__()
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

    def __str__(self):
        return "in_memory"


class _RealDatabase(Database):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "real"


def database_provider(in_memory: bool) -> Database:
    if in_memory:
        return _InMemoryDatabase()
    else:
        return _RealDatabase()


class Storage:
    """ Interface that makes it known to the caller whether the required standings are in the storage or not """
    def __init__(self, database: Database):
        self.database = database

    def contains_standings(self, key):
        return self.database.contains_key(key)

    def get(self, key):
        return self.database.get(key)

    def store(self, key, standings: Standings):
        self.database.store(key, standings)
