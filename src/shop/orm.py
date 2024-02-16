from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Date,
    create_engine,
)
from sqlalchemy.orm import mapper, registry, relationship
from shop.model import OrderLine, Batch
from sqlalchemy_utils import database_exists, create_database
import sys

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
    line_mapper = mapper_registry.map_imperatively(OrderLine, order_line)
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
