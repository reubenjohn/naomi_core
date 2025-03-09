import os
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


DB_PATH = os.environ.get("DB_PATH", "sqlite:///db.sqlite")

Base: Any = declarative_base()
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Database setup
def initialize_db():
    import naomi_core.db.agent  # noqa
    import naomi_core.db.chat  # noqa
    import naomi_core.db.property  # noqa
    import naomi_core.db.webhook  # noqa

    Base.metadata.create_all(engine)


def wipe_db():
    Base.metadata.drop_all(engine)
    initialize_db()


# Save message to database
def get_all_tables():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table';"))
        return [(name, sql) for name, sql in result]
