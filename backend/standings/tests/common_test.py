from unittest import TestCase

from backend.standings.common import _config


class CommonTestCases(TestCase):
    def test_raises_filenotfound_if_file_does_not_exist(self):
        self.assertRaises(FileNotFoundError, _config, "somefile.txt")

    def test_returns_valid_type_when_file_exists(self):
        conf = _config('test_files/test_config.json')
        self.assertTrue(conf is not None, "Must return config")
