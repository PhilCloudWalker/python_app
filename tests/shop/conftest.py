import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from shop.adapter.orm import DB_URL, metadata, start_mappers


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
            sqlite_session.execute(
                    "INSERT INTO products (sku, version_number) VALUES "
                    f"('{sku}', 0) "
                    "On CONFLICT DO NOTHING"
                )
            eta = f"'{eta}'" if eta else "NULL"
            sqlite_session.execute(
                "INSERT INTO batches (reference, sku,_purchased_quantity, eta) VALUES "
                f"('{batch_ref}', '{sku}', {qty}, {eta})"
            )
        sqlite_session.commit()

    return _add_stock


@pytest.fixture
def in_memory_db_session():
    engine = create_engine("sqlite:///:memory:", echo=True)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def memory_sessionfactory(in_memory_db_session):
    start_mappers()
    yield sessionmaker(bind=in_memory_db_session)
    clear_mappers()
