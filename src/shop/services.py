import shop.model as model


class InvalidSku(Exception):
    """Invalid sku error"""


def allocate(order_line, repo, session):
    batches = repo.list()

    if order_line.sku not in {b.sku for b in batches}:
        raise InvalidSku(f"Invalid sku {order_line.sku}")

    batch_ref = model.allocate(order_line, batches)
    session.commit()
    return batch_ref


def add_batch(reference, sku, qty, eta, repo, session):
    batch = model.Batch(ref=reference, sku=sku, eta=eta, qty=qty)
    repo.add(batch)
    session.commit()


def deallocate(order_line, batch, repo, session):
    batch.deallocate(order_line)
    repo.add(batch)
    session.commit()
