from . import app_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


engine = create_engine(app_config.DB_URI, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
