import pytest
from sqlalchemy.orm import Session, clear_mappers, sessionmaker
from sqlalchemy import create_engine
from shop.orm import metadata, start_mappers
from shop.orm import DB_URL


@pytest.fixture(scope="module")
def in_memory_db():
    engine = create_engine("sqlite:///:memory:", echo=True)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    connection = in_memory_db.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    transaction.rollback()
    connection.close()
    clear_mappers()


@pytest.fixture(scope="module")
def sqlite_db():
    engine = create_engine(DB_URL, echo=True)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session(sqlite_db):
    start_mappers()
    yield sessionmaker(bind=sqlite_db)()
    clear_mappers()


@pytest.fixture
def add_stock(sqlite_session):
    def _add_stock(batches):
        for batch_ref, sku, qty, eta in batches:
            eta = f'"{eta}"' if eta else "NULL"
            sqlite_session.execute(
                "INSERT INTO batches (reference, sku,_purchased_quantity, eta) VALUES "
                f'("{batch_ref}", "{sku}", {qty}, {eta})'
            )
        sqlite_session.commit()

    return _add_stock
