import os
import os.path
from file_manager.core import app_config


def scan_fs(path, include_root=False):
    """Return 2 lists: folders with configs and with no configs"""
    config_paths = []
    no_config_paths = []
    for (dirpath, _, filenames) in os.walk(path):
        if dirpath == path and not include_root:
            continue
        rel_path = os.path.relpath(dirpath, app_config.ROOT_PATH)
        if app_config.CONFIG_NAME in filenames:
            config_paths.append(rel_path)
        else:
            no_config_paths.append(rel_path)
    return config_paths, no_config_paths


def has_config(relpath):
    conf_path = os.path.join(app_config.ROOT_PATH, relpath, app_config.CONFIG_NAME)
    return os.path.exists(conf_path)
