import shop.model as model
import shop.repository as repository


def test_repository_can_save_a_batch(db_session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(db_session)
    repo.add(batch)
    db_session.commit()

    rows = db_session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(session):
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty)"
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )
    [[orderline_id]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


def insert_batch(db_session, batch_id):
    db_session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        'VALUES (:batch_id, "GENERIC-SOFA", 100, NULL)',
        dict(batch_id=batch_id),
    )
    [[reference]] = db_session.execute(
        "SELECT reference FROM batches WHERE reference=:batch_id",
        dict(batch_id=batch_id),
    )
    return reference


def insert_allocation(db_session, orderline_id, batch_id):
    db_session.execute(
        "INSERT INTO allocations (batch_id, orderline_id) VALUES (:batch_id, :orderline_id)",
        dict(batch_id=batch_id, orderline_id=orderline_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(db_session):
    orderline_id = insert_order_line(db_session)
    batch1_id = insert_batch(db_session, "batch1")
    insert_batch(db_session, "batch2")
    insert_allocation(db_session, orderline_id, batch1_id)  # (2)

    repo = repository.SqlAlchemyRepository(db_session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference  #(3)
    assert retrieved.sku == expected.sku 
    assert retrieved._purchased_quantity == expected._purchased_quantity

    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
