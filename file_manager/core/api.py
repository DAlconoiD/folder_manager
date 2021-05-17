import os
from . import app_config
from .config_manager.models import Config
from .config_manager.fs_operations import scan_fs
from .config_manager.config_rw import parse_config, write_config_to_file
from .db_operations import (create_folder_from_cfg, create_all, drop_all, create_attribute,
                            get_all_folder_ids, get_attribute_values, update_folder,
                            get_attr_list, get_folders, search_by_attributes)
from shutil import copytree, rmtree


def search_cfgs(filter_dict=None):
    cfgs = None
    if filter_dict is None or len(filter_dict) == 0:
        folders = get_folders()
        cfgs = [Config(f.name, f.date, f.version, f.path, f.id)
                for f in folders]
    else:
        attrs = []
        for attr, values in filter_dict.items():
            for value in values:
                attrs.append((attr, value))
        rows = search_by_attributes(attrs)
        cfgs = [Config(r[1], r[3], r[4], r[2], r[0]) for r in rows]
    return cfgs


def make_if_not_exists():
    """Makes DB if it is does not exist"""
    if not os.path.exists(app_config.DB_FP):
        print('MAKE DB')
        make_db()


def make_db():
    """Check all config files in root directory and make or update database out of this configs"""
    clear_db()
    create_all()
    write_attr()
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
    print(f'SRC:\n{src}\nDEST:\n{dest}')
    try:
        copytree(src, dest)
    except Exception as err:
        print('ERROR')
        raise err
    write_new_config(cfg)


def publish_and_remove(src, dest, cfg):
    publish_folder()
    remove_folder(src)


def remove_folder(p):
    try:
        rmtree(p, ignore_errors=True)
    except Exception as err:
        raise err
