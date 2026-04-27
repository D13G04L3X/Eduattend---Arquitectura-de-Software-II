# src/notification_service/infrastructure/config/db_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

Base = declarative_base()


def build_session_factory(database_url: str):
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    return scoped_session(
        sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    )
