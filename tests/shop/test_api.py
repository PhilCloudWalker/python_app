import pytest
import random_word
import random
import string
import requests
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from shop.orm import DB_URL
from config import AppConfig

Config = AppConfig.from_environ()


def random_sku():
    return random_word.RandomWords().get_random_word()


def random_batchref():
    return "".join(random.sample(string.ascii_lowercase, 3))


def random_orderid():
    return "".join(random.sample(string.ascii_lowercase, 4))


def add_stock(batches):
    engine = create_engine(DB_URL, echo=True)
    session = Session(bind=engine)
    for batch_ref, sku, qty, eta in batches:
        eta = f'"{eta}"' if eta else "NULL"
        session.execute(
            "INSERT INTO batches (reference, sku,_purchased_quantity, eta) VALUES "
            f'("{batch_ref}", "{sku}", {qty}, {eta})'
        )
    session.commit()
    session.close()


# @pytest.mark.usefixtures("restart_api")
# def test_api_returns_allocation(add_stock):
def test_api_returns_allocation():
    sku, othersku = random_sku(), random_sku()
    earlybatch = random_batchref()
    laterbatch = random_batchref()
    otherbatch = random_batchref()
    add_stock(
        [
            (laterbatch, sku, 100, "2011-01-02"),
            (earlybatch, sku, 100, "2011-01-01"),
            (otherbatch, othersku, 100, None),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = Config.url

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


# @pytest.mark.usefixtures("restart_api")
def test_400_message_for_out_of_stock():
    sku, small_batch, large_order = random_sku(), random_batchref(), random_orderid()
    add_stock(
        [
            (small_batch, sku, 10, "2011-01-01"),
        ]
    )
    data = {"orderid": large_order, "sku": sku, "qty": 20}
    url = Config.url
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Out of stock for sku {sku}"


def test_400_message_for_invalid_sku():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
    url = Config.url
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
