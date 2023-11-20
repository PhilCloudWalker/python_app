from shop.models import OrderLine, Order, Batch


def test_init_order_lines():
    lines = OrderLine(sku="abc", qty=1)
    assert lines.sku == "abc"
    assert lines.qty == 1


def test_init_order():
    order = Order(id="123", lines=[OrderLine("A1", 1), OrderLine("A2", 2)])
    assert order.id == "123"
    assert order.lines[0].sku == "A1"
    assert order.lines[0].qty == 1


def test_init_batch():
    batch = Batch(id="B1", sku="P1", qty=3, eta=0)
    assert batch.id == "B1"
    assert batch.sku == "P1"
    assert batch.qty == 3
    assert batch.eta == 0


def test_allocate_in_stock():
    batch = Batch(id="B1", sku="SMALL-TABLE", qty=20)
    line = OrderLine("SMALL-TABLE", qty=2)

    batch.allocate_order_line(line)
    assert batch.qty == 18


def test_allocate_not_possible():
    batch = Batch(id="B1", sku="BLUE-CUSHION", qty=1)
    line = OrderLine("BLUE-CUSHION", qty=2)

    batch.allocate_order_line(line)
    assert batch.qty == 2


def test_double_allocation():
    batch = Batch(id="B1", sku="BLUE-VASE", qty=10)
    line = OrderLine("BLUE-VASE", qty=2)

    batch.allocate_order_line(line)
    batch.allocate_order_line(line)

    assert batch.qty == 8
