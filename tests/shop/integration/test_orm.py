from datetime import date

import shop.domain.model as model


def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute('SELECT orderid, sku, qty FROM "order_lines"'))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES "
        '("order1", "RED-CHAIR", 12),'
        '("order1", "RED-TABLE", 13),'
        '("order2", "BLUE-LIPSTICK", 14)'
    )
    expected = [
        model.OrderLine("order1", "RED-CHAIR", 12),
        model.OrderLine("order1", "RED-TABLE", 13),
        model.OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    assert session.query(model.OrderLine).all() == expected


def test_batch_mapper_can_load_batches(session):
    session.execute(
        "INSERT INTO batches (reference, sku, eta, _purchased_quantity) VALUES "
        '("ref1", "IN-STOCK", NULL, 100),'
        '("ref2", "ON-THE-WAY", "2022-02-24", 50)'
    )
    expected = [
        model.Batch("ref1", "IN-STOCK", 100, None),
        model.Batch("ref2", "ON-THE-WAY", 50, date(2022, 2, 24)),
    ]
    assert session.query(model.Batch).all() == expected


def test_product_mapper_can_load_products(session):
    session.execute(
        "INSERT INTO batches (reference, sku, eta, _purchased_quantity) VALUES "
        '("ref1", "BLUE-BERRY",NULL, 100)'
    )
    session.execute(
        "INSERT INTO products (sku, version_number) VALUES "
        '("BLUE-BERRY", 0)'
    )

    product = session.query(model.Product).one()
    assert product.sku == "BLUE-BERRY"
    assert product._batches == [model.Batch("ref1", "BLUE-BERRY", 100, eta=None)]

def test_saving_products(session):
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    product = model.Product("sku1", [batch])
    session.add(product)
    session.commit()

    product_row = session.execute(
        'SELECT * FROM "products"'
    )
    batch_row = session.execute(
        'SELECT sku FROM "batches"'
    )
    assert list(product_row) == [("sku1", 0)]
    assert list(batch_row) == [("sku1",)]


def test_saving_batches(session):
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    session.add(batch)
    session.commit()

    rows = session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    )
    assert list(rows) == [("batch1", "sku1", 100, None)]


def test_saving_allocations(session):
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    line = model.OrderLine("order1", "sku1", 10)

    batch.allocate(line)
    session.add(batch)
    session.commit()

    rows = list(session.execute('SELECT batch_id FROM "order_lines"'))
    assert rows == [("batch1",)]


def test_update_batch_with_allocations(session):
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    session.add(batch)
    session.commit()

    line = model.OrderLine("order1", "sku1", 10)
    batch.allocate(line)
    session.add(batch)
    session.commit()

    rows = list(session.execute('SELECT batch_id FROM "order_lines"'))
    assert rows == [("batch1",)]
    batches = session.query(model.Batch).all()
    assert len(batches) == 1


def test_retrieving_allocations(session):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty, batch_id) VALUES ("order1", "sku1", 12, "batch1")'
    )

    batch = session.query(model.Batch).one()
    assert batch._allocations == {model.OrderLine("order1", "sku1", 12)}
