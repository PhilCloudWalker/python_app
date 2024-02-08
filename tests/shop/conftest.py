import pytest
from sqlalchemy.orm import Session, clear_mappers
from sqlalchemy import create_engine
from shop.orm import metadata, start_mappers


@pytest.fixture(scope="module")
def local_engine():
    engine = create_engine("sqlite:///:memory:", echo=True)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(local_engine):
    start_mappers()
    connection = local_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
    clear_mappers()
