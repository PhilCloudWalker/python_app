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
from sqlalchemy.engine import URL

from shop.domain.model import Batch, OrderLine, Product

from config import AppConfig

Config = AppConfig.from_environ()

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
DB_URL = URL.create(
    Config.db_driver,
    username=Config.db_user,
    password=Config.db_password,
    host=Config.db_host,
    database=Config.db_database,
)



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
    Column("sku", String, ForeignKey("products.sku")),
    Column("eta", Date),
    Column("_purchased_quantity", Integer),
)

product = Table(
    "products",
    metadata,
    Column("sku", String, primary_key=True),
    Column("version_number", Integer)
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
    mapper_registry.map_imperatively(
        Product, 
        product, 
        properties={
            "_batches": relationship(
                Batch, backref="batches", collection_class=list
            )
        }
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
