import logging
import pathlib
import subprocess
from config import load_config


class Repository:
    def __init__(self, name: str, path: pathlib.Path):
        self.name = name
        self.path = path


class RepositoryMethodLevel(Repository):
    def __init__(self, name: str, path: pathlib.Path):
        super().__init__(name, path)


def to_method_level_files(repository: Repository, output_repository_path: pathlib.Path):
    """
    processing the source code files in a repository, where for each file,
     each method extracted as a single file and the others (i.e. fields) are stored in one file
     using the git-stein https://github.com/sh5i/git-stein as core
    :param output_repository_path:
    :param repository:
    :return:
    """
    git_stein_path = load_config()["git-stein"]
    command = f"java -jar {git_stein_path}git-stein.jar {str(repository.path)} -o {str(output_repository_path)} @historage-jdt --no-original --no-classes --no-fields"

    logging.info(msg="running command: {}".format(command))
    print(command)
    subprocess.getoutput(command)
    logging.info(msg="finished command: {}".format(command))

