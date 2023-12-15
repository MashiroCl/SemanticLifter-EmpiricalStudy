import json
import logging


def load_config():
    with open("config.json", "r") as f:
        data = json.load(f)
    return data


def logging_config(log_file_path: str = "./commit_collect.log"):
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
