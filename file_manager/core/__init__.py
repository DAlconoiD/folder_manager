import configparser
import os

APP_CONFIG = 'appconf.ini'

class AppConfig():
    def __init__(self):
        self.APP_PATH = os.path.normpath(os.path.dirname(__file__)).rsplit(os.sep, 2)[0]
        # parse config
        p = os.path.join(self.APP_PATH, APP_CONFIG)
        config = configparser.ConfigParser()
        config.read(p, encoding='utf-8')
        #s = config.get('Settings', 'root')
        self.ROOT_PATH = config.get('Settings', 'root', fallback=os.getcwd())
        self.DATE_FORMAT = config.get('Settings', 'date_format', fallback='%Y-%m-%d') 
        self.CONFIG_NAME = config.get('Settings', 'date_format', fallback='!conf.ini')
        db_name = config.get('Settings', 'database', fallback='db.db')
        self.DB_URI = 'sqlite:///' + os.path.join(self.APP_PATH, db_name)

        #get predefined tags
        self.predefined_attrs = set()
        attrs = config.get('Settings', 'predefined_attrs', fallback='')
        if attrs != None:
            self.predefined_attrs = set(v.strip() for v in attrs.split(','))
        print(f'PATH: {p}, {__file__}')
        print(f'Config:\n{self}')
        


    def __repr__(self) -> str:
        return f'{self.ROOT_PATH}\n{self.CONFIG_NAME}\n{self.DATE_FORMAT}\n{self.DB_URI}\n{self.predefined_attrs}'

app_config = AppConfig()
