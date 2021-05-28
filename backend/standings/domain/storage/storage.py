from abc import ABC

from backend.standings.common import logger_factory
from backend.standings.domain.response.standings import Standings
from redis import Redis


class RedisCache:
    """ This class sets up a connection to a Redis server and puts and retrieves data from the cache """
    def __init__(self, host="localhost", port=6379, db=0):
        self.redis_client = Redis(host=host, port=port, db=db)

    def put(self, key: str, standings: Standings):
        self.redis_client.set(key, standings)

    def get(self, key: str) -> Standings:
        return self.redis_client.get(key)


class MongoDB:
    """ This class creates a connection to a mongodb server and makes it possible to write and put data to the db"""
    def __init__(self):
        pass

    def write(self, key, standings: Standings):
        pass

    def read(self, key: str) -> Standings:
        pass


class Database:
    def __init__(self):
        self.logger = logger_factory(Database.__name__)
        self.logger.info("Using {} database", self)

    def store(self, key: str, standings: Standings):
        self._raise_not_implemented()

    def contains_key(self, key: str):
        self._raise_not_implemented()

    def get(self, key):
        self._raise_not_implemented()

    def __str__(self):
        self._raise_not_implemented()

    def _raise_not_implemented(self):
        raise NotImplementedError("Method not implemented")

    @staticmethod
    def is_in_memory(database_type):
        is_supported = database_type == "in_memory" or database_type == "real_database"
        if not is_supported:
            raise ValueError("Unknown database type: {}".format(database_type))
        return database_type == "in_memory"


class _InMemoryDatabase(Database):
    """ This is an in memory database implementation which is not persistent and will mainly be used for testing """
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
    """Implementation of a real database that will facilitate saving and retrieving data from a distributed cache and
    from the database """
    def __init__(self, redis_cache: RedisCache, mongo_db: MongoDB):
        super().__init__()
        self.redis_cache = redis_cache
        self.mongo_db = mongo_db

    def __str__(self):
        return "real"


def database_provider(in_memory: bool, redis_cache=None, mongo_db=None) -> Database:
    if in_memory:
        return _InMemoryDatabase()
    else:
        return _RealDatabase(redis_cache, mongo_db)


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
