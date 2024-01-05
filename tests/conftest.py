import pytest
from shop.orm import metadata, start_mappers
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy import create_engine


@pytest.fixture
def in_memory_engine():
    engine = create_engine("sqlite:///")
    metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(in_memory_engine):
    start_mappers()
    yield sessionmaker(bind=in_memory_engine)()
    clear_mappers()
