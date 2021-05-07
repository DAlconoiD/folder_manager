import os
import datetime
import configparser
from .models import Config
from . import ROOT_PATH, CONFIG_FILE_NAME
from file_manager.core import DATE_FORMAT


def parse_config(rel_path):
    config = configparser.ConfigParser()
    p = os.path.join(ROOT_PATH, rel_path, CONFIG_FILE_NAME)
    config.read(p, encoding='utf-8')
    id = config.getint('General', 'id', fallback=None)
    name = config.get('General', 'name', fallback=None)
    date_str = config.get('General', 'date', fallback=None)
    date = datetime.datetime.strptime(date_str, DATE_FORMAT).date()
    ver = config.get('General', 'ver', fallback=None)
    path = config.get('General', 'path', fallback=rel_path)
    cfg = Config(name, date, ver, path, id)
    if config.has_section('Description'):
        description = config['Description']
        attributes = {}
        for key in description:
            values = list(v.strip() for v in description.get(key).split(','))
            attributes[key] = values
        if attributes:
            cfg.attributes = attributes
    if config.has_section('Special'):
        special_section = config['Special']
        special = {}
        for key in special_section:
            special[key] = special_section.get(key)
        cfg.special = special
    return cfg


def write_config_to_file(rel_path, cfg):
    config = configparser.ConfigParser()

    config['General'] = {}
    general = config['General']
    if cfg.id != None:
        general['id'] = str(cfg.id)
    general['name'] = cfg.name
    general['date'] = cfg.date.strftime(DATE_FORMAT)
    general['ver'] = cfg.ver
    general['path'] = cfg.path

    config['Description'] = {}
    attr_section = config['Description']
    if cfg.attributes:
        for key, values in cfg.attributes.items():
            attr_section[key] = ','.join(values)

    config['Special'] = {}
    spec_section = config['Special']
    if cfg.special:
        for key, value in cfg.special.items():
            spec_section[key] = value
    with open(os.path.join(ROOT_PATH, rel_path, CONFIG_FILE_NAME), 'w', encoding='utf-8') as configfile:
        config.write(configfile)


def get_attributes_only(rel_path, dct):
    if rel_path != '':
        path = os.path.join(ROOT_PATH, rel_path, CONFIG_FILE_NAME)
        print(path)
        if os.path.isfile(path):
            cfg = parse_config(rel_path)
            print(cfg)
            for name, values in cfg.attributes.items():
                if name not in dct:
                    dct[name] = set()
                v = dct.get(name)
                v.update(values)
        rel_path = os.path.dirname(os.path.normpath(rel_path))
        get_attributes_only(rel_path, dct)
    return dct
