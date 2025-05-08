from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config.settings import PostgresSettings


def new_session_maker(settings: PostgresSettings):
    engine = create_engine(settings.psycopg_dsn)
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
