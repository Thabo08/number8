from unittest import TestCase

from backend.standings.common import config


class CommonTestCases(TestCase):
    def test_raises_filenotfound_if_file_does_not_exist(self):
        self.assertRaises(FileNotFoundError, config, "somefile.txt")

    def test_returns_valid_type_when_file_exists(self):
        import os
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_config = os.path.abspath(os.path.join(test_dir, 'test_files/test_config.json'))
        conf = config(test_config)
        self.assertTrue(conf is not None, "Must return config")
