from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


class OutOfStock(Exception):
    pass

class WrongSku(Exception):
    pass

class NoAllocation(Exception):
    pass



@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()  # type: Set[OrderLine]

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
    
class Product: 

    def __init__(self, sku:str, batches:list) -> None:
        self.sku = sku
        self.batches = batches
        self.version_number = 0

        if wrong_batches := [b for b in batches if b.sku != self.sku ]:
            raise WrongSku(f"Attempt to allocate sku {wrong_batches[0].sku} to product {self.sku}")
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return False        
        return self.sku == other.sku

    def __repr__(self) -> str:
        return f"<Product {self.sku}>"
    
    def __hash__(self) -> int:
        return hash(self.sku)

    def add_batch(self, batch: Batch):

        if batch.sku != self.sku:
            raise WrongSku(f"Attempt to allocate sku {batch.sku} to product {self.sku}")

        self.batches.append(batch)

    def get_batch(self, reference):
        try:
            return next(b for b in self.batches if b.reference == reference)
        except StopIteration:
            return None

    def allocate(self, line: OrderLine):
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            raise OutOfStock(f"Out of stock for sku {line.sku}")
    
    def deallocate(self, line: OrderLine):
        try:
            batch = next(b for b in self.batches if line in b._allocations)
            batch.deallocate(line)
        except StopIteration:
            raise NoAllocation(f"Orderline {line.orderid} is not allocated")
