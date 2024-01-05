from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import mapper, relationship

import shop.model as model

engine = create_engine("sqlite:///foo.db")

metadata = MetaData()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

batches = Table(
    "batches",
    metadata,
    Column("reference", String, primary_key=True),
    Column("sku", String),
    Column("_purchased_quantity", Integer),
    Column("eta", Date),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("batch_id", ForeignKey("batches.reference")),
    Column("orderline_id", ForeignKey("order_lines.id")),
)


def start_mappers():
    lines_mapper = mapper(model.OrderLine, order_lines)
    mapper(model.Batch, batches, properties={
        "_allocations": relationship(lines_mapper, secondary=allocations, collection_class=set,)
    })
