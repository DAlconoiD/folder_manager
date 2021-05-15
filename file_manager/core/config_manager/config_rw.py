import os
import datetime
import configparser
from .models import Config
from file_manager.core import app_config


def parse_config(rel_path):
    config = configparser.ConfigParser()
    p = os.path.join(app_config.ROOT_PATH, rel_path, app_config.CONFIG_NAME)
    config.read(p, encoding='utf-8')
    id = config.getint('General', 'id', fallback=None)
    name = config.get('General', 'name', fallback=None)
    date_str = config.get(
        'General', 'date', fallback=str(datetime.date.today()))
    date = datetime.datetime.strptime(date_str, app_config.DATE_FORMAT).date()
    ver = config.get('General', 'ver', fallback=None)
    path = config.get('General', 'path', fallback=rel_path)
    cfg = Config(name, date, ver, path, id)
    attributes = {}
    if config.has_section('Description'):
        description = config['Description']
        for key in description:
            values = set(v.strip() for v in description.get(key).split(','))
            attributes[key] = values
    cfg.attributes = attributes
    special = {}
    if config.has_section('Special'):
        special_section = config['Special']
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
    general['date'] = cfg.date.strftime(app_config.DATE_FORMAT)
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
    with open(os.path.join(app_config.ROOT_PATH, rel_path, app_config.CONFIG_NAME), 'w', encoding='utf-8') as configfile:
        config.write(configfile)


def get_attributes_only(rel_path, dct):
    if rel_path != '':
        path = os.path.join(app_config.ROOT_PATH, rel_path,
                            app_config.CONFIG_NAME)
        if os.path.isfile(path):
            cfg = parse_config(rel_path)
            for name, values in cfg.attributes.items():
                if name not in dct:
                    dct[name] = set()
                v = dct.get(name)
                v.update(values)
        rel_path = os.path.dirname(os.path.normpath(rel_path))
        get_attributes_only(rel_path, dct)
    return dct
