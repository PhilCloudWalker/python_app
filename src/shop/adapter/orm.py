from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.orm import Session, registry, relationship
from sqlalchemy_utils import create_database, database_exists

from shop.domain.model import Batch, OrderLine

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
DB_URL = "sqlite:///data.db"

order_line = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderid", String(50)),
    Column("sku", String(50)),
    Column("qty", Integer),
    Column("batch_id", String, ForeignKey("batches.reference")),
)

batch = Table(
    "batches",
    metadata,
    Column("reference", String, primary_key=True),
    Column("sku", String),
    Column("eta", Date),
    Column("_purchased_quantity", Integer),
)


def start_mappers():
    mapper_registry.map_imperatively(OrderLine, order_line)
    mapper_registry.map_imperatively(
        Batch,
        batch,
        properties={
            "_allocations": relationship(
                OrderLine, backref="order_lines", collection_class=set
            )
        },
    )


def validate_database():
    engine = create_engine(DB_URL, echo=True)
    if not database_exists(engine.url):  # Checks for the first time
        create_database(engine.url)  # Create new DB
        metadata.create_all(engine)
        print(
            f"New Database Created: {database_exists(engine.url)}"
        )  # Verifies if database is there or not.
    else:
        print("Database Already Exists")


def get_session():
    engine = create_engine(DB_URL, echo=True)
    return Session(bind=engine)
