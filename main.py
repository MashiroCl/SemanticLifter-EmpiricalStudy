import argparse
import pathlib

from collect_commit import extract_within_method_refactor_commit, Repository, detect_with_RefactoringMiner, load_config
from config import logging_config

# def analysis_within_method_ref(refactoringminer, repository_path, output_repository_path, output_json, RMresult_path):
#     commitInfos = extract_within_method_refactor_commit(repository_path, output_repository_path, output_json)
#     repo = Repository(repository_path)
#     for commitInfo in commitInfos:
#         detect_with_RefactoringMiner(refactoringminer, repo, commitInfo, RMresult_path)


def analysis_within_method_ref(refactoringminer, repository_path, output_repository_path):
    repo = Repository(repository_path)
    output_repository_path = pathlib.Path(output_repository_path)
    output_json, RMresult_path = build_directory(output_repository_path)
    commitInfos = extract_within_method_refactor_commit(repository_path, output_repository_path.joinpath(repo.name), output_json.joinpath("withinmethod_refactor_commits.json"))
    for commitInfo in commitInfos:
        detect_with_RefactoringMiner(refactoringminer, repo, commitInfo, RMresult_path)

def command():
    parser = argparse.ArgumentParser(description='Empirical Study of Semantic Lifter')
    parser.add_argument('--src', help="path for the source repository")
    parser.add_argument('--dst', help="path for the transfered method-level repository")
    # parser.add_argument('--co', help="output path for the within-method-ref-commit list")
    # parser.add_argument('--rmo',
    #                     help="output path for the RefactoringMiner detection results for the within-method-ref-commit "
    #                          "list")

    return parser.parse_args()


def build_directory(path:pathlib.Path):
    """
    Build the directory for the method_level repository
    -name of method_level repository
        -repository
        -within-method-ref-commit.json
        -RM
            -xxxxx.json
            -yyyyy.json

    :return:
    """
    rm_path = path.joinpath("RM")
    rm_path.mkdir(parents=True, exist_ok=False)
    return path, rm_path



if __name__ == "__main__":
    args = command()
    config = load_config()
    logging_config()
    analysis_within_method_ref(
        config["RefactoringMiner"],
        args.src,
        args.dst,
    )
