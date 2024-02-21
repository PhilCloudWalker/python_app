from flask import Flask, make_response, request
from shop.orm import validate_database, DB_URL, start_mappers
from shop.repository import SqlAlchemyRepository
import shop.model as model
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

app = Flask(__name__)
# app.before_request(validate_database)
engine = create_engine(DB_URL, echo=True)
validate_database()
start_mappers()  # TODO: best place to put?

MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB in bytes


@app.post("/allocate")
def allocate():
    session = Session(bind=engine)
    repo = SqlAlchemyRepository(session)
    batches = repo.list()

    if int(request.headers.get("Content-Length")) > MAX_CONTENT_LENGTH:
        raise make_response({"message": f"Request object has to be below 1MB"}, 400)

    data = request.get_json()
    order_line = model.OrderLine(data["orderid"], data["sku"], data["qty"])

    if not any([order_line.sku == b.sku for b in batches]):
        return make_response({"message": f"Invalid sku {order_line.sku}"}, 400)

    try:
        batch_ref = model.allocate(order_line, batches)
    except model.OutOfStock as exc:
        return make_response({"message": str(exc)}, 400)
    return make_response({"batchref": batch_ref}, 201)
