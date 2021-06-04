from redis import Redis
from pymongo import MongoClient

from backend.standings.common import equality_tester
from backend.standings.common import logger_factory
from backend.standings.domain.response.standings import Standings


class Key:
    """ Holds storage key """
    def __init__(self, alias, season):
        self.key = "{0}_{1}".format(alias, season)

    def __eq__(self, other):
        return equality_tester(self, Key, other)

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return self.key


class RedisCache:
    """ This class sets up a connection to a Redis server and puts and retrieves data from the cache """
    def __init__(self, host="localhost", port=6379, db=0):
        self.redis_client = Redis(host=host, port=port, db=db)
        self.logger = logger_factory(RedisCache.__name__)

        self.logger.info("Initialised Redis Cache on: %s:%s", host, port)

    def put(self, key: Key, standings: Standings):
        try:
            key = key.__str__()
            self.redis_client.set(key, standings)
            self.logger.debug("Inserted %s for key %s", standings, key)
        except Exception:
            self.logger.error("Could not insert %s for key %s", standings, key)
            raise Exception("Could not insert {} for key {}".format(standings, key))

    def get(self, key: Key) -> Standings:
        try:
            key = key.__str__()
            standings = self.redis_client.get(key)
            self.logger.debug("Retrieved %s for key %s from Redis Cache", standings, key)
            return standings
        except Exception:
            self.logger.error("Could not retrieve standings for key %s from Redis Cache", key)
            raise Exception("Could not retrieve standings for key {} from Redis Cache".format(key))


class MongoDB:
    """ This class creates a connection to a mongodb server and makes it possible to write and put data to the db"""
    def __init__(self, host="localhost", port=27017, database_name="standings", collection_name="static_standings"):
        """ Sets up a connection to mongodb """
        mongo_client = MongoClient("mongodb://{}:{}".format(host, port))
        database = mongo_client[database_name]
        self.collection = database[collection_name]

        self.logger = logger_factory(MongoDB.__name__)
        self.logger.info("Initialised MongoDB connection on: %s:%s", host, port)

    def write(self, key: Key, standings: Standings):
        try:
            entry = {"key": key, "standings": standings}
            result = self.collection.insert_one(entry)
            self.logger.debug("ID - %s: Inserted %s for key %s", result.inserted_id, standings, key)
        except Exception:
            self.logger.error("Could not insert %s for key %s", standings, key)
            raise Exception("Could not insert {} for key {}".format(standings, key))

    def read(self, key: Key) -> Standings:
        try:
            query = {"key": key.__str__()}  # todo: Check if we need to use key.__str()__ call here
            standings = self.collection.find_one(query)
            self.logger.debug("Retrieved %s for key %s from MongoDB", standings, key)
            return standings
        except Exception:
            self.logger.error("Could not retrieve standings for key %s from MongoDB", key)
            raise Exception("Could not retrieve standings for key {} from MongoDB".format(key))


class Database:
    def __init__(self):
        self.logger = logger_factory(Database.__name__)
        self.logger.info("Using {} database", self)

    def store(self, key: Key, standings: Standings):
        """ Stores value for key to database

            :param key Key for value
            :param standings Standings value to store
        """
        self._raise_not_implemented()

    def check_and_get(self, key: Key):
        """ Checks if a value for a given key exists and returns it if that's the case

            :param key Key for value
            :returns Tuple of bool (true) and Standings object if value exists, otherwise false and None
        """
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

    def store(self, key: Key, standings: Standings):
        self.logger.info("Storing standings for %s in memory database", key)
        self.database[key] = standings

    def check_and_get(self, key: Key):
        from_in_mem = self.database.get(key)
        exists = from_in_mem is not None
        message = "Standings for key {} exist".format(key if exists else key.__str__() + " does not ")
        self.logger.info(message)

        return exists, from_in_mem

    def __str__(self):
        return "in_memory"


class _RealDatabase(Database):
    """Implementation of a real database that will facilitate saving and retrieving data from a distributed cache and
    from the database """
    def __init__(self, redis_cache: RedisCache, mongo_db: MongoDB):
        super().__init__()
        self.redis_cache = redis_cache
        self.mongo_db = mongo_db

    def store(self, key: Key, standings: Standings):
        is_new_entry = self.redis_cache.get(key) is None and self.mongo_db.read(key) is None
        if is_new_entry:
            self.logger.info("Storing standings for %s in database and cache", key)
            self.mongo_db.write(key, standings)
            self.redis_cache.put(key, standings)
        else:
            from_db = self.mongo_db.read(key)
            if from_db is not None and from_db == standings:
                self.logger.info("Storing standings for %s in cache", key)
                self.redis_cache.put(key, standings)

    def check_and_get(self, key: Key):
        try:
            from_cache = self.redis_cache.get(key)
            in_cache = from_cache is not None
            if not in_cache:
                self.logger.info("Standings for %s not found in cache. Checking in database", key.__str__())
                from_db = self.mongo_db.read(key)
                if from_db is not None:
                    self.redis_cache.put(key, from_db)
                    from_cache = from_db
                    in_cache = True
            return in_cache, from_cache
        except Exception:
            self.logger.error("Error reading from storage for key: %s", key.__str__())
            raise Exception("Error reading from storage for key: " + key.__str__())

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

    def store(self, key: Key, standings: Standings):
        self.database.store(key, standings)

    def check_and_get(self, key: Key):
        return self.database.check_and_get(key)
