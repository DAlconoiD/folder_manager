from . import app_config
from .database import session, engine
from .models import Folder, AttributeValue, Attribute, Base
from .config_manager.fs_operations import scan_fs
from .config_manager.config_rw import parse_config, write_config_to_file
from .db_operations import (clear_db_data, create_folder_from_cfg, create_all, drop_all, create_attribute,
                            folder_exists, get_all_folder_ids, get_attribute_values, update_folder, get_attr_list)
from shutil import copytree


def get_folders(filter_dict=None):
    q = session.query(Folder)
    if filter_dict:
        for attr, value in filter_dict.items():
            q = q.filter(getattr(Folder, attr) == value)
    folders = q.all()
    return folders


def make_db():
    """Check all config files in root directory and make or update database out of this configs"""
    clear_db()
    create_all()
    has_conf, _ = scan_fs(app_config.ROOT_PATH)
    new_configs = []
    existing_ids = get_all_folder_ids()
    for p in has_conf:
        conf = parse_config(p)
        if conf.id != None:
            if conf.id not in existing_ids:
                id = create_folder_from_cfg(conf)
                conf.id = id
                write_config_to_file(p, conf)
            pass
        else:
            if conf.path != p:
                conf.path = p
                write_config_to_file(p, conf)
            new_configs.append(conf)
    for cfg in new_configs:
        id = create_folder_from_cfg(cfg)
        cfg.id = id
        write_config_to_file(cfg.path, cfg)
        pass


def clear_db():
    drop_all()

def write_attr():
    for attr in app_config.predefined_attrs:
        create_attribute(attr)

def attribute_values_list():
    attr_vals = {}
    attrs = get_attr_list()
    for attr in attrs:
        values = get_attribute_values(attr)
        attr_vals[attr] = values
    return attr_vals

def write_new_config(cfg):
    cfg.id = create_folder_from_cfg(cfg)
    write_config_to_file(cfg.path, cfg)
    return cfg.id


def update_config(cfg):
    update_folder(cfg)
    write_config_to_file(cfg.path, cfg)


def publish_folder(src, dest, cfg):
    try:
        copytree(src, dest)
    except Exception as err:
        raise err
    write_new_config(cfg)
