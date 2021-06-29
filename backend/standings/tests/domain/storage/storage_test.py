from unittest import TestCase
from unittest import mock

from backend.standings.domain.storage.storage import Database
from backend.standings.domain.storage.storage import Key
from backend.standings.domain.storage.storage import Storage
from backend.standings.domain.storage.storage import database_provider


def _test_storage(type_, redis_cache=None, mongodb=None):
    return Storage(database_provider(Database.is_in_memory(type_), redis_cache, mongodb))


class StorageTestCases(TestCase):

    def __init__(self, *args, **kwargs):
        super(StorageTestCases, self).__init__(*args, **kwargs)
        self.in_memory_storage = _test_storage("in_memory")
        self.key = Key("epl", "2020")

    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_contains_is_true_if_key_value_exists(self, mock_standings):
        # given
        self.in_memory_storage.store(self.key, mock_standings)
        in_cache, standings = self.in_memory_storage.check_and_get(self.key)

        # then
        self.assertTrue(in_cache)
        self.assertEqual(mock_standings, standings)

    def test_contains_is_false_if_key_value_does_not_exist(self):
        # given
        in_cache, _ = self.in_memory_storage.check_and_get(Key("rubbish", "year"))

        # then
        self.assertFalse(in_cache)

    @mock.patch('backend.standings.domain.response.standings.Standings')
    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_gets_different_standings_for_different_keys(self, epl, seriea):
        self.in_memory_storage.store(self.key, epl)
        seriea_key = Key("seriea", "2020")
        self.in_memory_storage.store(seriea_key, seriea)

        epl_exists, epl_standings = self.in_memory_storage.check_and_get(self.key)
        seriea_exists, seriea_standings = self.in_memory_storage.check_and_get(seriea_key)

        self.assertNotEqual(epl_standings, seriea_standings)

        self.assertEqual(epl_standings, self.in_memory_storage.check_and_get(self.key)[1])
        self.assertEqual(seriea_standings, self.in_memory_storage.check_and_get(seriea_key)[1])

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
    def test_should_return_true_if_value_for_key_exists_in_cache(self, redis_cache, mongodb, mock_standings):
        # given
        redis_cache.get.return_value = mock_standings

        # when
        real_db = _test_storage("real_database", redis_cache, mongodb)
        in_cache, standings = real_db.check_and_get(self.key)

        # then
        self.assertTrue(in_cache)
        self.assertEqual(mock_standings, standings)

    @mock.patch('backend.standings.domain.storage.storage.RedisCache')
    @mock.patch('backend.standings.domain.storage.storage.MongoDB')
    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_should_return_true_if_value_for_key_exists_in_db(self, redis_cache, mongodb, mock_standings):
        # given
        redis_cache.get.return_value = None
        mongodb.read.return_value = mock_standings

        # when
        real_db = _test_storage("real_database", redis_cache, mongodb)
        in_cache, standings = real_db.check_and_get(self.key)

        # then
        mongodb.read.assert_called_with(self.key)
        redis_cache.put.assert_called_with(self.key, mock_standings)
        self.assertTrue(in_cache)
        self.assertEqual(mock_standings, standings)

    @mock.patch('backend.standings.domain.storage.storage.RedisCache')
    @mock.patch('backend.standings.domain.storage.storage.MongoDB')
    def test_should_return_false_if_value_for_key_exists_nowhere(self, redis_cache, mongodb):
        # given
        redis_cache.get.return_value = None
        mongodb.read.return_value = None

        # when
        real_db = _test_storage("real_database", redis_cache, mongodb)
        in_cache, standings = real_db.check_and_get(self.key)

        # then
        self.assertFalse(in_cache)
        self.assertIsNone(standings)
