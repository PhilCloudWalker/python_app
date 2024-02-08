from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import mapper, registry, relationship
from shop.model import OrderLine, Batch

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

order_line = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderid", String(50)),
    Column("sku", String(50)),
    Column("qty", Integer),
    Column("batch_id", String, ForeignKey("batches.reference"))
)

batch = Table(
    "batches",
    metadata, 
    Column("reference", String, primary_key=True),
    Column("sku", String),
    Column("eta", DateTime),
    Column("_purchased_quantity", Integer)
)


def start_mappers():
    line_mapper = mapper_registry.map_imperatively(OrderLine, order_line)
    mapper_registry.map_imperatively(
        Batch, 
        batch, 
        properties ={
            "_allocations": relationship(OrderLine, backref="order_lines", collection_class=set)
        }
    )