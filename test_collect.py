import unittest
from collect_commit import *
from config import load_config, logging_config


class TestCollect(unittest.TestCase):
    def setUp(self):
        logging_config()
        self.config = load_config()
        self.repository_mbassador = Repository('mbassador', pathlib.Path(self.config["mbassador"]))
        self.method_level_repository_output_path = pathlib.Path(self.config["method_level_repository_output_path"])

    def test_to_method_level_files_mbassador(self):
        to_method_level_files(self.repository_mbassador, pathlib.Path(str(self.method_level_repository_output_path)+"/mbassador_finergit"))
