import shop.domain.model as model


class InvalidSku(Exception):
    """Invalid sku error"""

class NoProduct(Exception):
    """No product available"""


def allocate(orderid, sku, qty, uow):
    order_line = model.OrderLine(orderid, sku, qty)

    with uow:
        product = uow.products.get(sku=sku)
        if not product:
            raise InvalidSku(f"Invalid sku {order_line.sku}")
        batch_ref = product.allocate(order_line)

    return batch_ref


def add_batch(reference, sku, qty, eta, uow):
    batch = model.Batch(ref=reference, sku=sku, eta=eta, qty=qty)
    with uow:
        if product := uow.products.get(sku):
            product.add_batch(batch)
        else:
            uow.products.add(model.Product(sku,[batch]))
        uow.commit()


def deallocate(orderid, sku, qty, uow):
    with uow:
        product = uow.products.get(sku)
        if not product:
            raise NoProduct

        order_line = model.OrderLine(orderid, sku, qty)
        product.deallocate(order_line)
        uow.commit()


def reallocate(orderid, sku, qty, uow):
    with uow:
        product = uow.products.get(sku)
        order_line = model.OrderLine(orderid, sku, qty)
        product.deallocate(order_line)
        product.allocate(order_line)
        uow.commit()
