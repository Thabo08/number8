from unittest import TestCase
from unittest import mock

from backend.standings.domain.storage.storage import Database
from backend.standings.domain.storage.storage import Storage
from backend.standings.domain.storage.storage import database_provider


class StorageTestCases(TestCase):

    def __init__(self, *args, **kwargs):
        super(StorageTestCases, self).__init__(*args, **kwargs)
        self.in_memory_storage = Storage(database_provider(Database.is_in_memory("in_memory")))

    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_contains_is_true_if_key_value_exists(self, standings):
        self.in_memory_storage.store("epl_2020", standings)
        self.assertTrue(self.in_memory_storage.contains_standings("epl_2020"))

    def test_contains_is_false_if_key_value_does_not_exist(self):
        self.assertFalse(self.in_memory_storage.contains_standings("rubbish"))

    @mock.patch('backend.standings.domain.response.standings.Standings')
    @mock.patch('backend.standings.domain.response.standings.Standings')
    def test_gets_different_standings_for_different_keys(self, epl, seriea):
        self.in_memory_storage.store("epl_2020", epl)
        self.in_memory_storage.store("seriea_2020", seriea)

        epl_standings = self.in_memory_storage.get("epl_2020")
        seriea_standings = self.in_memory_storage.get("seriea_2020")

        self.assertNotEqual(epl_standings, seriea_standings)

        self.assertEqual(epl_standings, self.in_memory_storage.get("epl_2020"))
        self.assertEqual(seriea_standings, self.in_memory_storage.get("seriea_2020"))

    def test_should_write_to_cache_database_if_entry_does_not_exist(self):
        pass

    def test_should_get_value_from_cache_if_exists(self):
        pass

    def test_should_get_from_db_and_write_to_cache_if_only_in_db(self):
        pass
