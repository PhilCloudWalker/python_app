from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


@dataclass
class Batch:
    reference: str
    sku: str
    qty: int
    eta: int = Optional[date]
    allocated: List = field(default_factory=list)

    def allocate_order_line(self, line: OrderLine):
        if self.qty >= line.qty:
            if line.orderid not in self.allocated:
                self.qty -= line.qty
                self.allocated.append(line.orderid)


@dataclass
class Order:
    id: str
    lines: List[OrderLine]
