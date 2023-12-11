import logging
import pathlib
import subprocess
import re
from config import load_config
import json


class Repository:
    def __init__(self, path: pathlib.Path):
        self.path = path


class CommitInfo:
    def __init__(self, commitID: str, notes: str, message: list[str], change_status: list[str]):
        self.commitID = commitID
        self.notes = notes
        self.message = message
        self.change_status = change_status

    def __str__(self):
        return f'{self.commitID} - {self.notes}, {self.message} {self.change_status}'


def is_commit_sha1(line: str):
    pattern = re.compile(r'^[0-9a-fA-F]{40}$')
    return bool(pattern.match(line.strip()))


def is_commit_Notes(line: str, nextline: str) -> bool:
    """
    The Notes information in the method-level repo commit history
    e.g.
    Notes:
    499ae3a4a3beb4c20de6d856a3eadeb7aaa0119b
    :param line:
    :return:
    """
    if "Notes:" in line and is_commit_sha1(nextline):
        return True
    return False


def parse_commit_infoblock(infoblock: list[str]):
    res = {}
    if len(infoblock) < 1 or "commit" not in infoblock[0]:
        raise ValueError("parse commit error, infoblock: \n", infoblock)
    res["sha1"] = infoblock[0].split("commit ")[1]
    res["message"] = []
    res["files_status"] = []
    isafterNotes = False
    i=1
    while i < len(infoblock):
        infoblock[i] = infoblock[i].strip()

        # commit message
        if "Author: " in infoblock[i] and "Date:   " in infoblock[i + 1]:
            for j in range(i + 2, len(infoblock) - 1):
                if is_commit_Notes(infoblock[j], infoblock[j + 1]):
                    res["message"] = infoblock[i + 2:j - 1]
                    i = j
                    break

        # file status
        if isafterNotes:
            if len(infoblock[i]) > 0:
                res["files_status"].append(infoblock[i])

        # Notes
        if is_commit_Notes(infoblock[i - 1], infoblock[i]):
            res["Notes"] = infoblock[i].strip()
            isafterNotes = True
        i += 1
    return res


def seperate_by_commit(commitInfos):
    def is_commit_line(line, nextline):
        if "commit" in line \
                and len(line.split("commit ")) > 1 \
                and is_commit_sha1(line.split("commit ")[1]) \
                and "Author: " in nextline:
            return True
        return False

    infoblocks = []

    commitInfos = commitInfos.split("\n")
    i = 0

    # starts from "commit xxxx", ends at "Note: "
    while i < len(commitInfos) - 1:
        if is_commit_line(commitInfos[i], commitInfos[i + 1]):
            for j in range(i + 1, len(commitInfos)):
                # if j == len(commitInfos) - 1 or is_commit_line(commitInfos[j], commitInfos[j + 1]):
                if j == len(commitInfos) - 1 or is_commit_Notes(commitInfos[j], commitInfos[j + 1]):
                    infoblocks.append(commitInfos[i:j+2])
                    i = j + 2
                    break
        i += 1
    return infoblocks


def git_log_with_name_status(git_path: pathlib.Path):
    """
    git log on the repository and parse the commit history into a list of CommitInfo objects
    :param git_path: target method-level repository
    :return:
    """
    logging.info("git log " + str(git_path))
    command = f"git --git-dir {str(git_path)}/.git log --no-merges --name-status"
    commitHistory = subprocess.getoutput(command)

    logging.info("parsing commitInfos")
    commitInfos = []
    # seperate by commit
    infoblocks = seperate_by_commit(commitHistory)
    for infoblock in infoblocks:
        parsed = parse_commit_infoblock(infoblock)
        logging.info("parsing " + parsed["sha1"])
        commitInfos.append(CommitInfo(parsed["sha1"], parsed["Notes"], parsed["message"], parsed["files_status"]))

    logging.info(f"finished parsing {len(commitInfos)} commitInfos")

    return commitInfos


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
    subprocess.getoutput(command)
    logging.info(msg="finished command: {}".format(command))


def is_within_method_change(commitInfo: CommitInfo):
    if len(commitInfo.change_status) == 1 and "M\t" in commitInfo.change_status[0]:
        return True
    return False


def is_refactor_commit(commitInfo: CommitInfo):
    if len(commitInfo.message) > 0 and (any("refactor" in each for each in commitInfo.message)
                                        or any("restruct" in each for each in commitInfo.message)):
        return True
    return False


def is_mjava(commitInfo: CommitInfo):
    """
    in the change status, the changed file is *.mjava
    :param commitInfo:
    :return:
    """
    if len(commitInfo.change_status) > 0 and any(".mjava" in each for each in commitInfo.change_status):
        return True
    return False


def commit_info_decoder(obj):
    if obj.__class__ == CommitInfo.__class__:
        return CommitInfo(obj['commitID'], obj['notes'], obj["message"], obj['change_status'])
    return obj


def commit_info_encoder(obj):
    if isinstance(obj, CommitInfo):
        return {
            'commitID': obj.commitID,
            'notes': obj.notes,
            'message': obj.message,
            'change_status': obj.change_status
        }
    return obj


def extract_within_method_refactor_commit(repository_path, output_repository_path, within_method_refactor_json,
                                          commitInfo_output_json=None):
    repository_path = pathlib.Path(repository_path)
    output_repository_path = pathlib.Path(output_repository_path)

    if not output_repository_path.exists():
        to_method_level_files(Repository(repository_path), output_repository_path)
    commitInfos = git_log_with_name_status(output_repository_path)

    # write into json
    if commitInfo_output_json:
        with open(commitInfo_output_json, "w") as f:
            json.dump(commitInfos, f, default=commit_info_encoder)

    within_method_refactor = []

    for commitInfo in commitInfos:
        if is_within_method_change(commitInfo) and is_mjava(commitInfo) and is_refactor_commit(commitInfo):
            within_method_refactor.append(commitInfo)

    with open(within_method_refactor_json, "w") as f:
        json.dump(within_method_refactor, f, default=commit_info_encoder)

    logging.info(f"written {len(within_method_refactor)} into {within_method_refactor_json}")
