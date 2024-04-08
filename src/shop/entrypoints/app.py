from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

import shop.domain.model as model
import shop.service_layer.services as services
from shop.adapter.orm import start_mappers, validate_database, DB_URL
import shop.service_layer.unit_of_work as unit_of_work


app = FastAPI(root_path="/app")
validate_database()
start_mappers()  # TODO: potential test issue - if test import flask_app start mappers would be called a 2nd time after conftest which results in an error
MAX_CONTENT_LENGTH = 1024**2

class LineItem(BaseModel):
    orderid: str
    sku: str
    qty: int



@app.post("/allocate", status_code=201)
def allocate(request: Request, item: LineItem):
    if int(request.headers.get("Content-Length")) > MAX_CONTENT_LENGTH:
        raise HTTPException(status_code=400, detail= "Request object has to be below 1MB")

    uow = unit_of_work.SqlAlchemyUnitOfWork(sessionmaker(bind=create_engine(DB_URL, echo=True)))
    try:
        batch_ref = services.allocate(
            item.orderid, item.sku, item.qty, uow
        )
    except (model.OutOfStock, services.InvalidSku) as exc:
        raise HTTPException(status_code=400, detail= str(exc))
    return {"batchref": batch_ref}

@app.get("/products")
def list_products():
    uow = unit_of_work.SqlAlchemyUnitOfWork(sessionmaker(bind=create_engine(DB_URL, echo=True)))
    with uow:
        products = uow.products.list()
    return ([p.sku for p in products], 200)



@app.get("/health")
def health():
    return {"message": "Hello World"}

@app.get("/")
def health():
    return {"message": "Hello, this is the homepage"}
