from shop.models import OrderLine, Order, Batch


def test_init_order_lines():
    line = OrderLine("order1", sku="abc", qty=1)
    assert line.orderid == "order1"
    assert line.sku == "abc"
    assert line.qty == 1


def test_init_order():
    order = Order(id="order1", lines=[OrderLine("order1", "A1", 1), OrderLine("order1","A2", 2)])
    assert order.id == "order1"
    assert order.lines[0].sku == "A1"
    assert order.lines[0].qty == 1


def test_init_batch():
    batch = Batch(reference="B1", sku="P1", qty=3, eta=0)
    assert batch.reference == "B1"
    assert batch.sku == "P1"
    assert batch.qty == 3
    assert batch.eta == 0


def test_allocate_in_stock():
    batch = Batch(reference="B1", sku="SMALL-TABLE", qty=20)
    line = OrderLine("order1", "SMALL-TABLE", qty=2)

    batch.allocate_order_line(line)
    assert batch.qty == 18


def test_allocate_not_possible():
    batch = Batch(reference="B1", sku="BLUE-CUSHION", qty=1)
    line = OrderLine("order1", "BLUE-CUSHION", qty=2)

    batch.allocate_order_line(line)
    assert batch.qty == 1


def test_allocation_is_idempotent():
    batch = Batch(reference="B1", sku="BLUE-VASE", qty=10)
    line = OrderLine("order1", "BLUE-VASE", qty=2)

    batch.allocate_order_line(line)
    batch.allocate_order_line(line)

    assert batch.qty == 8
