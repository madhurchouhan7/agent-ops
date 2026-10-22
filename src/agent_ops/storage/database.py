"""Database engine creation and session factory utilities."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from agent_ops.storage.models import Base


def create_db_engine(database_url: str = "sqlite:///:memory:") -> Engine:
    """Create a SQLAlchemy database engine."""
    connect_args: dict[str, Any] = {}
    kwargs: dict[str, Any] = {}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if ":memory:" in database_url:
            kwargs["poolclass"] = StaticPool
        else:
            kwargs["poolclass"] = NullPool

    return create_engine(database_url, connect_args=connect_args, **kwargs)


def init_db(engine: Engine) -> None:
    """Create all configured tables in the target database."""
    Base.metadata.create_all(bind=engine)


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a sessionmaker bound to the given engine."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session(
    session_factory: sessionmaker[Session],
) -> Generator[Session, None, None]:
    """Provide a transactional database session context."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
