import random
import string

import random_word
import requests

from config import AppConfig

Config = AppConfig.from_environ()


def random_sku():
    return random_word.RandomWords().get_random_word()


def random_batchref():
    return "".join(random.sample(string.ascii_lowercase, 3))


def random_orderid():
    return "".join(random.sample(string.ascii_lowercase, 4))


def test_api_returns_allocation(add_stock):
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


def test_400_message_for_out_of_stock(add_stock):
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


def test_400_content_too_long():
    very_long_order_id = "long" * 400000
    data = {"orderid": very_long_order_id, "sku": "LONG", "qty": 20}
    url = Config.url
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Request object has to be below 1MB"
