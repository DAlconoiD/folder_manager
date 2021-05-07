from datetime import date
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table
from sqlalchemy.orm import relationship
from .database import Base


folder_value = Table(
    'folder_value', Base.metadata,
    Column('folder_id', Integer, ForeignKey('folders.id')),
    Column('value_id', Integer, ForeignKey('attribute_values.id'))
)


class Folder(Base):
    __tablename__ = 'folders'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    path = Column(String)
    date = Column(Date, default=date.today)
    version = Column(String, default='0')

    values = relationship(
        'AttributeValue',
        secondary=folder_value,
        back_populates='folders')

    def __init__(self, name, path, date, version):
        self.name = name
        self.path = path

        if date == None:
            self.date = date.today
        else:
            self.date = date

        if version == None:
            self.version = 0
        else:
            self.version = version

    def __repr__(self):
        return "Folder <id='%s', name='%s', path='%s', date='%s', version='%s'>" \
            % (self.id, self.name, self.path, self.date, self.version)


class Attribute(Base):
    __tablename__ = 'attributes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    values = relationship(
        'AttributeValue', back_populates='attribute', cascade='all, delete, delete-orphan')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Attribute <id='%s', name='%s'>" % (self.id, self.name)


class AttributeValue(Base):
    __tablename__ = 'attribute_values'

    id = Column(Integer, primary_key=True, index=True)
    attr_id = Column(Integer, ForeignKey('attributes.id'))
    value = Column(String)

    attribute = relationship('Attribute', back_populates='values')
    folders = relationship(
        'Folder',
        secondary=folder_value,
        back_populates='values')

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Attribute Value <id='%s', name='%s'>" % (self.id, self.value)
