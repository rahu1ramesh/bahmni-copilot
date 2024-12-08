import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

SQL_ALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

db_engine = create_engine(SQL_ALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()


def create_tables(bases: list[declarative_base], db_engine):
    for base in bases:
        base.metadata.create_all(bind=db_engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
