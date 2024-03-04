import shop.domain.model as model


class InvalidSku(Exception):
    """Invalid sku error"""


def allocate(orderid, sku, qty, uow):
    order_line = model.OrderLine(orderid, sku, qty)

    with uow:
        batches = uow.batches.list()
        if order_line.sku not in {b.sku for b in batches}:
            raise InvalidSku(f"Invalid sku {order_line.sku}")
        batch_ref = model.allocate(order_line, batches)

    return batch_ref


def add_batch(reference, sku, qty, eta, uow):
    batch = model.Batch(ref=reference, sku=sku, eta=eta, qty=qty)
    with uow:
        uow.batches.add(batch)
        uow.commit()


def deallocate(orderid, sku, qty, batch, uow):
    order_line = model.OrderLine(orderid, sku, qty)
    batch.deallocate(order_line)
    with uow:
        uow.batches.add(batch)
        uow.commit()


def reallocate(orderid, sku, qty, uow):
    with uow:
        batches = uow.batches.list()
        order_line = model.OrderLine(orderid, sku, qty)
        batch = next(b for b in batches if order_line in b._allocations)
        batch.deallocate(order_line)
        model.allocate(order_line, batches)
        uow.commit()
