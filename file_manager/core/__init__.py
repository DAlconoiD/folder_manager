import configparser
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

APP_CONFIG = 'appconf.ini'

class AppConfig():
    def __init__(self):
        # parse config
        config = configparser.ConfigParser()
        config.read(APP_CONFIG, encoding='utf-8')
        self.ROOT_PATH = r'C:\Users\Егор\Desktop\Test'
        self.ROOT_PATH = config.get('Settings', 'root', fallback=os.getcwd())
        self.DATE_FORMAT = config.get('Settings', 'date_format', fallback='%Y-%m-%d') 
        self.CONFIG_NAME = config.get('Settings', 'date_format', fallback='!conf.ini')
        db_name = config.get('Settings', 'database', fallback='db.db')
        self.DB_URI = 'sqlite:///' + db_name
        print(f'Config:\n{self}')


    def __repr__(self) -> str:
        return f'{self.ROOT_PATH}\n{self.CONFIG_NAME}\n{self.DATE_FORMAT}\n{self.DB_URI}'

app_config = AppConfig()
