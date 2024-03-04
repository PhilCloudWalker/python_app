import datetime as dt

import pytest

import shop.domain.model as model
import shop.service_layer.services as services
from shop.service_layer.unit_of_work import AbstractUnitOfWork


class FakeRepository:
    def __init__(self, batches) -> None:
        self._batches = set(batches)

    @classmethod
    def for_batch(cls, ref, sku, qty, eta):
        return FakeRepository([model.Batch(ref, sku, qty, eta)])

    def list(self):
        return self._batches

    def add(self, batch):
        if batch in self._batches:
            self._batches.remove(batch)
            self._batches.add(batch)
        else:
            self._batches.add(batch)

    def get(self, batch_id):
        return next(b for b in self._batches if b.reference == batch_id)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def rollback(self):
        pass

    def commit(self):
        self.committed = True


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("b1") is not None
    # assert session.committed


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


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_deallocate_decrements_available_quantity():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, uow)
    services.allocate("o1", "BLUE-PLINTH", 10, uow)
    batch = uow.batches.get(batch_id="b1")
    assert batch.available_quantity == 90
    services.deallocate("o1", "BLUE-PLINTH", 10, batch, uow)
    assert batch.available_quantity == 100


def test_trying_to_deallocate_unallocated_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, uow)
    batch = uow.batches.get(batch_id="b1")
    services.deallocate("o1", "RRED-PLINTH", 10, batch, uow)
    assert batch.available_quantity == 100


def test_prefers_warehouse_batches_to_shipments():
    tomorrow = dt.datetime.today() + dt.timedelta(days=1)
    uow = FakeUnitOfWork()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, None, uow)
    services.add_batch("shipment-batch", "RETRO-CLOCK", 100, tomorrow, uow)

    services.allocate("o1", "RETRO-CLOCK", 10, uow)

    in_stock_batch = uow.batches.get("in-stock-batch")
    shipment_batch = uow.batches.get("shipment-batch")
    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_reallocate_order():
    tomorrow = dt.datetime.today() + dt.timedelta(days=1)
    uow = FakeUnitOfWork()

    services.add_batch("on-the-way", "RETRO-CLOCK", 100, tomorrow, uow)
    services.allocate("o1", "RETRO-CLOCK", 10, uow)
    shipment_batch = uow.batches.get("on-the-way")
    assert shipment_batch.available_quantity == 90

    services.add_batch("just-found", "RETRO-CLOCK", 200, tomorrow, uow)
    services.reallocate("o1", "RETRO-CLOCK", 10, uow)

    in_stock_batch = uow.batches.get("just-found")
    shipment_batch = uow.batches.get("on-the-way")
    assert in_stock_batch.available_quantity == 190
    assert shipment_batch.available_quantity == 100
