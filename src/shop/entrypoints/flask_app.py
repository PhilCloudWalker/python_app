from flask import Flask, make_response, request
from shop.adapter.orm import validate_database, DB_URL, start_mappers
from shop.adapter.repository import SqlAlchemyRepository
import shop.domain.model as model
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import shop.service_layer.services as services
from shop.config import AppConfig

app = Flask(__name__)
get_session = sessionmaker(bind=create_engine(DB_URL, echo=True))
validate_database()
start_mappers()  # TODO: best place to put?
Config = AppConfig.from_environ()
MAX_CONTENT_LENGTH = 1024^2


@app.post("/allocate")
def allocate():
    session = get_session()
    repo = SqlAlchemyRepository(session)

    if int(request.headers.get("Content-Length")) > MAX_CONTENT_LENGTH:
        return make_response({"message": "Request object has to be below 1MB"}, 400)

    data = request.get_json()

    try:
        batch_ref = services.allocate(data["orderid"], data["sku"], data["qty"], repo, session)
    except (model.OutOfStock, services.InvalidSku) as exc:
        return make_response({"message": str(exc)}, 400)
    return make_response({"batchref": batch_ref}, 201)
