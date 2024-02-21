import shop.model as model

class InvalidSku(Exception):
    """Invalid sku error"""


def allocate(order_line, repo, session):
    batches = repo.list()

    if not any([order_line.sku == b.sku for b in batches]):
        raise InvalidSku(f"Invalid sku {order_line.sku}")

    batch_ref = model.allocate(order_line, batches)
    session.commit()
    return batch_ref
