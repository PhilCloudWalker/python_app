from dataclasses import dataclass, field
from typing import List, Optional, Set
from datetime import date


class OutOfStock(Exception):
    """Out of stock"""

@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


@dataclass
class Batch:

    def __init__(self, reference: str, sku: str, qty: int, eta: Optional[date] = None):
        self.reference = reference
        self.sku = sku
        self._purchased_quantity = qty
        self.eta = eta
        self._allocations = set()


    def allocate_order_line(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)
    
    def can_allocate(self, line: OrderLine):
        return self.available_quantity >= line.qty and self.sku == line.sku

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)
    
    @property
    def _allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int :
        return self._purchased_quantity - self._allocated_quantity

    def __gt__(self, other):
        if self.eta is None: 
            return False
        if other.eta is None:
            return True
        else:
            return self.eta > other.eta


@dataclass
class Order:
    id: str
    lines: List[OrderLine]

def allocate(line: OrderLine, batches: List[Batch]):
    try:
        b = next(b for b in sorted(batches) if b.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"Out of stock {line.sku}")
    b.allocate_order_line(line)
    return b.reference
