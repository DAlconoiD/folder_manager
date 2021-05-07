from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATE_FORMAT = '%Y-%m-%d'


class AppCore():
    def __init__(self):
        # parse config
        self.DATE_FORMAT = '%Y-%m-%d'
        self.ROOT_PATH = r'C:\Users\Егор\Desktop\Test'
        self.CONFIG_NAME = '!conf.ini'
        self.DB_URI = 'sqlite:///test1.db'


app = AppCore()
