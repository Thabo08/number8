from unittest import TestCase
from unittest import mock

from backend.standings.domain.storage.storage import Database
from backend.standings.domain.storage.storage import Storage
from backend.standings.domain.storage.storage import database_provider


def _test_storage(type_, redis_cache=None, mongodb=None):
    return Storage(database_provider(Database.is_in_memory(type_), redis_cache, mongodb))


class StorageTestCases(TestCase):

    def __init__(self, *args, **kwargs):
        super(StorageTestCases, self).__init__(*args, **kwargs)
        self.in_memory_storage = _test_storage("in_memory")
        self.key = "epl_2020"

    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_contains_is_true_if_key_value_exists(self, standings):
        self.in_memory_storage.store(self.key, standings)
        self.assertTrue(self.in_memory_storage.contains_standings(self.key))

    def test_contains_is_false_if_key_value_does_not_exist(self):
        self.assertFalse(self.in_memory_storage.contains_standings("rubbish"))

    @mock.patch('backend.standings.domain.response.standings.Standings')
    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_gets_different_standings_for_different_keys(self, epl, seriea):
        self.in_memory_storage.store(self.key, epl)
        self.in_memory_storage.store("seriea_2020", seriea)

        epl_standings = self.in_memory_storage.get(self.key)
        seriea_standings = self.in_memory_storage.get("seriea_2020")

        self.assertNotEqual(epl_standings, seriea_standings)

        self.assertEqual(epl_standings, self.in_memory_storage.get(self.key))
        self.assertEqual(seriea_standings, self.in_memory_storage.get("seriea_2020"))

    @mock.patch('backend.standings.domain.storage.storage.RedisCache')
    @mock.patch('backend.standings.domain.storage.storage.MongoDB')
    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_should_write_to_cache_and_database_if_entry_does_not_exist(self, redis_cache, mongodb, mock_standings):
        # given
        redis_cache.get.return_value = None
        mongodb.read.return_value = None

        # when
        real_db = _test_storage("real_database", redis_cache, mongodb)
        real_db.store(self.key, mock_standings)

        # then
        redis_cache.put.assert_called_with(self.key, mock_standings)
        mongodb.write.assert_called_with(self.key, mock_standings)

    @mock.patch('backend.standings.domain.storage.storage.RedisCache')
    @mock.patch('backend.standings.domain.storage.storage.MongoDB')
    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_should_write_only_to_cache_if_entry_only_exist_in_db(self, redis_cache, mongodb, mock_standings):
        # given
        redis_cache.get.return_value = None
        mongodb.read.return_value = mock_standings

        # when
        real_db = _test_storage("real_database", redis_cache, mongodb)
        real_db.store(self.key, mock_standings)

        # then
        redis_cache.put.assert_called_with(self.key, mock_standings)
        mongodb.write.assert_not_called()

    @mock.patch('backend.standings.domain.storage.storage.RedisCache')
    @mock.patch('backend.standings.domain.storage.storage.MongoDB')
    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_should_return_true_if_value_is_in_cache(self, redis_cache, mongodb, mock_standings):
        # given
        redis_cache.get.return_value = mock_standings
        real_db = _test_storage("real_database", redis_cache, mongodb)

        # then
        self.assertTrue(real_db.contains_standings(self.key))

    @mock.patch('backend.standings.domain.storage.storage.RedisCache')
    @mock.patch('backend.standings.domain.storage.storage.MongoDB')
    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_should_get_value_from_cache_if_exists(self, redis_cache, mongodb, mock_standings):
        # given
        redis_cache.get.return_value = mock_standings
        mongodb.read.return_value = None

        # when
        real_db = _test_storage("real_database", redis_cache, mongodb)
        standings = real_db.get(self.key)

        # then
        self.assertEqual(mock_standings, standings)

