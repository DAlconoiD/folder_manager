import datetime
from sqlalchemy import inspect
from . import app_config
from .database import session, engine
from .models import Folder, AttributeValue, Attribute, Base


def create_all():
    Base.metadata.create_all(bind=engine)


def drop_all():
    Base.metadata.drop_all(bind=engine)


def create_folder_from_cfg(cfg):
    folder = Folder(name=cfg.name,
                    path=cfg.path,
                    date=cfg.date,
                    version=cfg.ver)
    bind_values_to_folder(cfg, folder)
    session.add(folder)
    session.commit()
    return folder.id


def update_folder(cfg):
    folder = session.query(Folder).filter_by(id=cfg.id).first()
    folder.values = []
    bind_values_to_folder(cfg, folder)
    folder.name = cfg.name
    folder.path = cfg.path
    folder.date = cfg.date
    folder.version = cfg.ver
    session.commit()


def create_attribute(name):
    attribute = Attribute(name)
    session.add(attribute)
    session.commit()
    return attribute


def create_attribute_value(attr_name, val):
    attr = session.query(Attribute).filter(
        Attribute.name == attr_name).first()
    if attr != None:
        attr_val = AttributeValue(val)
        attr.values.append(attr_val)
        session.commit()
        return attr_val
    return None


def bind_values_to_folder(cfg, folder):
    if cfg.attributes != None:
        for name, values in cfg.attributes.items():
            attr = get_attribute(name)
            if attr == None:
                attr = create_attribute(name)
            for v in values:
                val = get_attribute_value(name, v)
                if val == None:
                    val = create_attribute_value(name, v)
                folder.values.append(val)


def get_attribute(name):
    attr = session.query(Attribute).filter_by(name=name).first()
    return attr


def get_attribute_values(name):
    attr = session.query(Attribute).filter_by(name=name).first()
    attr_values = set(a.value for a in attr.values)
    return attr_values


def get_attr_list():
    attrs = session.query(Attribute.name).all()
    return set(a[0] for a in attrs)


def get_attribute_value(name, value):
    val = session.query(AttributeValue).join(Attribute).\
        filter(Attribute.name == name).\
        filter(AttributeValue.value == value).first()
    return val


def get_folders(filter_dict=None):
    q = session.query(Folder)
    if filter_dict:
        for attr, value in filter_dict.items():
            q = q.filter(getattr(Folder, attr) == value)
    folders = q.all()
    return folders


def folder_exists(id):
    folder = session.query(Folder).filter_by(id=id).first()
    return bool(folder)


def get_all_folder_ids():
    ids = session.query(Folder.id).all()
    id_list = list([id[0] for id in ids])
    return id_list


def clear_db_data():
    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
        print(f'Clear table {table}')
    session.commit()

