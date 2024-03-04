from flask import Flask, make_response, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import shop.domain.model as model
import shop.service_layer.services as services
from shop.adapter.orm import start_mappers, validate_database, DB_URL
import shop.service_layer.unit_of_work as unit_of_work


app = Flask(__name__)
validate_database()
start_mappers()  # TODO: potential test issue - if test import flask_app start mappers would be called a 2nd time after conftest which results in an error
MAX_CONTENT_LENGTH = 1024**2


@app.post("/allocate")
def allocate():
    if int(request.headers.get("Content-Length")) > MAX_CONTENT_LENGTH:
        return make_response({"message": "Request object has to be below 1MB"}, 400)

    data = request.get_json()

    uow = unit_of_work.SqlAlchemyUnitOfWork(sessionmaker(bind=create_engine(DB_URL, echo=True)))
    try:
        batch_ref = services.allocate(
            data["orderid"], data["sku"], data["qty"], uow
        )
    except (model.OutOfStock, services.InvalidSku) as exc:
        return make_response({"message": str(exc)}, 400)
    return make_response({"batchref": batch_ref}, 201)
