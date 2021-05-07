import os
import os.path
from . import ROOT_PATH, CONFIG_FILE_NAME


def scan_fs(path, include_root=False):
    """Return 2 lists: folders with configs and with no configs"""
    config_paths = []
    no_config_paths = []
    for (dirpath, _, filenames) in os.walk(path):
        if dirpath == path and not include_root:
            continue
        rel_path = os.path.relpath(dirpath, ROOT_PATH)
        if CONFIG_FILE_NAME in filenames:
            config_paths.append(rel_path)
        else:
            no_config_paths.append(rel_path)
    return config_paths, no_config_paths


def has_config(relpath):
    conf_path = os.path.join(ROOT_PATH, relpath, CONFIG_FILE_NAME)
    return os.path.exists(conf_path)
