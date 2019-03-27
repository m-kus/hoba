import os
import unittest
from unittest.mock import patch

from hoba.cli import load_config
from hoba.gen import generate_files


def get_sample_path(filename):
    return os.path.join(os.path.dirname(__file__), 'data', filename)


class HobaGenTests(unittest.TestCase):

    @patch('hoba.gen.pass_show')
    def test_gen(self, pass_show):
        config = load_config(get_sample_path('sample_0.yml'))
        pass_show.return_value = 'test'
        generate_files(config, 'prod')
