import json
import os

DEFAULT_CONFIG = {
    "log_dir": "./logs",
    "output_dir": "./reports",
    "thresholds": {
        "zombie_days": 30,
        "edge_call_threshold": 10,
        "edge_dept_threshold": 1,
        "slow_threshold": 5.0,
        "error_threshold": 0.05,
        "core_call_threshold": 100,
        "core_dept_threshold": 2
    }
}

CONFIG_FILE = os.environ.get('DINGDONG_CONFIG', './dingdong_config.json')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)