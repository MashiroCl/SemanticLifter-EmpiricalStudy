import json
import logging


def load_config():
    with open("config.json", "r") as f:
        data = json.load(f)
    return data


def logging_config():
    logging.basicConfig(filename=load_config()["log_file"], level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
