import json
import os

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".chess_ai_config.json")


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            pass
    return {}


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
            json.dump(cfg, handle, indent=2)
    except Exception:
        pass
