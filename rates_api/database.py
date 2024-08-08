from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from rates_api.config import settings

engine = create_engine(settings.database_url.unicode_string())
session_factory = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
