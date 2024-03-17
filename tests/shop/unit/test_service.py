import datetime as dt

import pytest

import shop.domain.model as model
import shop.service_layer.services as services
from shop.service_layer.unit_of_work import AbstractUnitOfWork

class FakeRepository:
    def __init__(self, products) -> None:
        self._products = set(products)

    @classmethod
    def for_batch(cls, ref, sku, qty, eta):
        return FakeRepository([model.Batch(ref, sku, qty, eta)])

    def list(self):
        return self._products

    def add(self, product): # old
        if product in self._products:
            self._products.remove(product)
            self._products.add(product)
        else:
            self._products.add(product)

    def get(self, sku):
        try: 
            return next(p for p in self._products if p.sku == sku)
        except StopIteration:
            return None

#TODO adjust to product
class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def rollback(self):
        pass

    def commit(self):
        self.committed = True


def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.committed

def test_add_batch_for_existing_product():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "GARISH-RUG", 100, None, uow)
    services.add_batch("b2", "GARISH-RUG", 99, None, uow)
    assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG")._batches]

def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed

def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_deallocate_decrements_available_quantity():
    uow = FakeUnitOfWork()
    services.add_batch("in-stock-batch", "BLUE-PLINTH", 100, None, uow)
    services.allocate("o1", "BLUE-PLINTH", 10, uow)
    product = uow.products.get("BLUE-PLINTH")
    batch = product.get_batch("in-stock-batch")
    assert batch.available_quantity == 90
    services.deallocate("o1", "BLUE-PLINTH", 10, uow)
    assert batch.available_quantity == 100


def test_trying_to_deallocate_unallocated_batch():
    uow = FakeUnitOfWork()
    with pytest.raises(services.NoProduct):
        services.deallocate("o1", "RRED-PLINTH", 10, uow)


def test_prefers_warehouse_batches_to_shipments():
    tomorrow = dt.datetime.today() + dt.timedelta(days=1)
    uow = FakeUnitOfWork()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, None, uow)
    services.add_batch("on-the-way", "RETRO-CLOCK", 100, tomorrow, uow)

    services.allocate("o1", "RETRO-CLOCK", 10, uow)

    product = uow.products.get("RETRO-CLOCK")
    in_stock_batch = product.get_batch("in-stock-batch")
    shipment_batch = product.get_batch("on-the-way")
    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_reallocate_order():
    tomorrow = dt.datetime.today() + dt.timedelta(days=1)
    uow = FakeUnitOfWork()

    services.add_batch("on-the-way", "RETRO-CLOCK", 100, tomorrow, uow)
    services.allocate("o1", "RETRO-CLOCK", 10, uow)
    product = uow.products.get("RETRO-CLOCK")
    shipment_batch = product.get_batch("on-the-way")
    assert shipment_batch.available_quantity == 90

    services.add_batch("just-found", "RETRO-CLOCK", 200, None, uow)
    services.reallocate("o1", "RETRO-CLOCK", 10, uow)

    in_stock_batch = product.get_batch("just-found")
    shipment_batch = product.get_batch("on-the-way")
    assert in_stock_batch.available_quantity == 190
    assert shipment_batch.available_quantity == 100
