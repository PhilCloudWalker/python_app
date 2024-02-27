import shop.domain.model as model


class InvalidSku(Exception):
    """Invalid sku error"""


def allocate(orderid, sku, qty, repo, session):
    batches = repo.list()
    order_line = model.OrderLine(orderid, sku, qty)

    if order_line.sku not in {b.sku for b in batches}:
        raise InvalidSku(f"Invalid sku {order_line.sku}")

    batch_ref = model.allocate(order_line, batches)
    session.commit()
    return batch_ref


def add_batch(reference, sku, qty, eta, repo, session):
    batch = model.Batch(ref=reference, sku=sku, eta=eta, qty=qty)
    repo.add(batch)
    session.commit()


def deallocate(orderid, sku, qty, batch, repo, session):
    order_line = model.OrderLine(orderid, sku, qty)
    batch.deallocate(order_line)
    repo.add(batch)
    session.commit()
