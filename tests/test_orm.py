import shop.model as model


def test_orderline_papper_can_load_lines(db_session):
    db_session.execute(
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

    assert db_session.query(model.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(db_session):
    new_line = model.OrderLine("order1", "DECORATIVE-WIDGET", 12)
    db_session.add(new_line)
    db_session.commit()

    rows = list(db_session.execute('Select orderid, sku, qty FROM "order_lines"'))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]
