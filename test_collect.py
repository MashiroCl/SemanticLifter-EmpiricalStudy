import unittest
# from collect_commit import *
import pathlib
from collect_commit import (Repository, to_method_level_files, parse_commit_infoblock,
                            git_log_with_name_status, extract_within_method_refactor_commit,
                            is_refactor_commit, is_mjava ,CommitInfo)
from config import load_config, logging_config



class TestCollect(unittest.TestCase):
    def setUp(self):
        logging_config()
        self.config = load_config()
        self.repository_mbassador = Repository(pathlib.Path(self.config["mbassador"]))
        self.method_level_repository_output_path = pathlib.Path(self.config["method_level_repository_output_path"])
        self.repository_presto = Repository(pathlib.Path(self.config["presto"]))
        self.repository_jetuml = Repository(pathlib.Path(self.config["jetuml"]))
        self.repository_cascading = Repository(pathlib.Path(self.config["cascading"]))
        self.repository_blueflood = Repository(pathlib.Path(self.config["blueflood"]))


    def test_to_method_level_files_mbassador(self):
        to_method_level_files(self.repository_mbassador, pathlib.Path(str(self.method_level_repository_output_path)+"/mbassador_finergit"))


    def test_parse_commit_infoblock(self):
        infoblock = """commit c7d38a48fd4577103c53b82eea80452e4f6c8f71
                    Author: Viacheslav Kolybelkin <kolybelkin@gmail.com>
                    Date:   Thu Sep 26 13:42:18 2019 +0400
                    
                        Made it possible to extend MessagePublication class
                    
                    Notes:
                        521ce6e6d96c238b14eb2e0c83e5ffadba8c3785
                    
                    """
        res = parse_commit_infoblock(infoblock.split("\n"))
        self.assertEqual(res["sha1"], "c7d38a48fd4577103c53b82eea80452e4f6c8f71")
        self.assertEqual(res["Notes"], "521ce6e6d96c238b14eb2e0c83e5ffadba8c3785")
        self.assertEqual(len(res["change_status"]), 0)

    def test_parse_commit_infoblock2(self):
        infoblock = """commit c0a1f84cef0ff7ba6cb80cd3b0498b3ff9d604d2
                    Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
                    Date:   Tue Oct 13 06:50:00 2020 +0000
                    Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
                    Date:   Tue Oct 13 06:50:00 2020 +0000
                    
                        Bump junit from 4.12 to 4.13.1
                        
                        Bumps [junit](https://github.com/junit-team/junit4) from 4.12 to 4.13.1.
                        - [Release notes](https://github.com/junit-team/junit4/releases)
                        - [Changelog](https://github.com/junit-team/junit4/blob/main/doc/ReleaseNotes4.12.md)
                        - [Commits](https://github.com/junit-team/junit4/compare/r4.12...r4.13.1)
                        
                        Signed-off-by: dependabot[bot] <support@github.com>
                    
                    Notes:
                        499ae3a4a3beb4c20de6d856a3eadeb7aaa0119b
                    
                    M       pom.xml
                    
                    """
        res = parse_commit_infoblock(infoblock.split("\n"))
        self.assertEqual(res["sha1"], "c0a1f84cef0ff7ba6cb80cd3b0498b3ff9d604d2")
        self.assertEqual(res["Notes"], "499ae3a4a3beb4c20de6d856a3eadeb7aaa0119b")
        self.assertEqual(len(res["change_status"]), 1)


    def test_git_log_with_name_status(self):
        data = git_log_with_name_status(self.method_level_repository_output_path.joinpath("mbassador_finergit"))
        self.assertEqual(len(data), 671)

    def test_is_refactor_commit_positive(self):
        res = is_refactor_commit(CommitInfo("123", "123", ['', '    Small refactorings with minor API changes. Increased test coverage'], "123"))
        self.assertTrue(res)

    def test_is_refactor_commit_negative(self):
        res = is_refactor_commit(CommitInfo("123", "123", ["this is a refatoring", "lalala"], "123"))
        self.assertFalse(res)

    def test_is_mjava_positive(self):
        res = is_mjava(CommitInfo("123", "123", ["this is a refatoring", "lalala"], "M\ttest.mjava"))
        self.assertFalse(res)

    def test_is_mjava_positive(self):
        res = is_mjava(CommitInfo("123", "123", ["this is a refatoring", "lalala"], "M\ttest.xml"))
        self.assertFalse(res)

    def test_extract_within_method_change_commit_mbassador(self):
        data = extract_within_method_refactor_commit(self.repository_mbassador.path,
                                                   self.method_level_repository_output_path.joinpath("mbassador_finergit"),
                                                   self.method_level_repository_output_path.joinpath("mbassador_withinmethod.json"))

    def test_extract_within_method_change_commit_presto(self):
            data = extract_within_method_refactor_commit(self.repository_presto.path,
                                                         self.method_level_repository_output_path.joinpath(
                                                             "presto_finergit"),
                                                         self.method_level_repository_output_path.joinpath(
                                                             "presto_withinmethod_refactor.json"))

    def test_extract_within_method_change_commit_jetuml(self):
            data = extract_within_method_refactor_commit(self.repository_jetuml.path,
                                                         self.method_level_repository_output_path.joinpath(
                                                             "jetuml_finergit"),
                                                         self.method_level_repository_output_path.joinpath(
                                                             "jetuml_withinmethod_refactor.json"))

    def test_extract_within_method_change_commit_cascading(self):
            data = extract_within_method_refactor_commit(self.repository_cascading.path,
                                                         self.method_level_repository_output_path.joinpath(
                                                             "cascading_finergit"),
                                                         self.method_level_repository_output_path.joinpath(
                                                             "cascading_withinmethod_refactor.json"))

    def test_extract_within_method_change_blueflood(self):
            data = extract_within_method_refactor_commit(self.repository_blueflood.path,
                                                         self.method_level_repository_output_path.joinpath(
                                                             "blueflood_finergit"),
                                                         self.method_level_repository_output_path.joinpath(
                                                             "blueflood_withinmethod_refactor.json"))