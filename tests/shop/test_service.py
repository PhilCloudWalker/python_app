import pytest
import shop.model as model
import shop.services as services


class FakeRepository:
    def __init__(self, batches) -> None:
        self._batches = set(batches)

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
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    line = model.OrderLine("o1", "BLUE-PLINTH", 10)
    services.allocate(line, repo, session)
    batch = repo.get(batch_id="b1")
    assert batch.available_quantity == 90
    services.deallocate(line, batch, repo, session)
    assert batch.available_quantity == 100

def test_trying_to_deallocate_unallocated_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    batch = repo.get(batch_id="b1")
    line = model.OrderLine("o1", "RRED-PLINTH", 10)
    services.deallocate(line, batch, repo, session)
    assert batch.available_quantity == 100