import datetime as dt

import pytest

import shop.domain.model as model
import shop.service_layer.services as services


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


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    repo = FakeRepository.for_batch("batch1", "COMPLICATED-LAMP", 100, eta=None)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "batch1"


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_error_for_invalid_sku():
    repo = FakeRepository.for_batch("b1", "AREALSKU", 100, eta=None)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo = FakeRepository.for_batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    session = FakeSession()

    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    services.allocate("o1", "BLUE-PLINTH", 10, repo, session)
    batch = repo.get(batch_id="b1")
    assert batch.available_quantity == 90
    services.deallocate("o1", "BLUE-PLINTH", 10, batch, repo, session)
    assert batch.available_quantity == 100


def test_trying_to_deallocate_unallocated_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    batch = repo.get(batch_id="b1")
    services.deallocate("o1", "RRED-PLINTH", 10, batch, repo, session)
    assert batch.available_quantity == 100


def test_prefers_warehouse_batches_to_shipments():
    tomorrow = dt.datetime.today() + dt.timedelta(days=1)
    repo = FakeRepository.for_batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    session = FakeSession()
    services.add_batch("shipment-batch", "RETRO-CLOCK", 100, tomorrow, repo, session)

    services.allocate("o1", "RETRO-CLOCK", 10, repo, session)

    in_stock_batch = repo.get("in-stock-batch")
    shipment_batch = repo.get("shipment-batch")
    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
