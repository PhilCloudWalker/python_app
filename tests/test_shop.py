from shop.model import OrderLine, Order, Batch, allocate, OutOfStock
from datetime import date, timedelta
import pytest


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-1", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )


def test_init_order_lines():
    line = OrderLine("order1", sku="abc", qty=1)
    assert line.orderid == "order1"
    assert line.sku == "abc"
    assert line.qty == 1


def test_init_order():
    order = Order(
        id="order1", lines=[OrderLine("order1", "A1", 1), OrderLine("order1", "A2", 2)]
    )
    assert order.id == "order1"
    assert order.lines[0].sku == "A1"
    assert order.lines[0].qty == 1


def test_init_batch():
    batch = Batch(reference="B1", sku="P1", qty=3, eta=0)
    assert batch.reference == "B1"
    assert batch.sku == "P1"
    assert batch.available_quantity == 3
    assert batch.eta == 0


def test_allocate_in_stock():
    batch, line = make_batch_and_line("SMALL-TABLE", batch_qty=20, line_qty=2)
    batch.allocate_order_line(line)
    assert batch.available_quantity == 18


def test_allocate_not_possible():
    batch, line = make_batch_and_line("BLUE-CUSHION", batch_qty=1, line_qty=2)
    assert batch.can_allocate(line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("BLUE-VASE", batch_qty=10, line_qty=2)

    batch.allocate_order_line(line)
    batch.allocate_order_line(line)

    assert batch.available_quantity == 8


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-1", "SKU-BATCH", 10)
    line = OrderLine("order-123", "OTHER-SKU", 2)

    assert batch.can_allocate(line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_allocate_and_deallocate_lines():
    batch, line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.allocate_order_line(line)
    assert batch.available_quantity == 18
    batch.deallocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == 20


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch(
        "shipment-batch", "RETRO-CLOCK", 100, eta=date.today() + timedelta(days=1)
    )
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [shipment_batch, in_stock_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=date.today())
    medium = Batch(
        "normal-batch", "MINIMALIST-SPOON", 100, eta=date.today() + timedelta(days=1)
    )
    latest = Batch(
        "slow-batch", "MINIMALIST-SPOON", 100, eta=date.today() + timedelta(days=2)
    )
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch(
        "shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=date.today()
    )
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raise_error_if_out_of_stock():
    batch, line = make_batch_and_line("BLUE-CUSHION", batch_qty=1, line_qty=2)

    with pytest.raises(OutOfStock):
        allocate(line, [batch])
