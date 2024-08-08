from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:ratestask@localhost/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_factory = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
