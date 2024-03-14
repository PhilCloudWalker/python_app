from shop.domain.model import Batch, Product
from typing import Optional


class AbstractRepository:
    def add(self, session):
        raise NotImplementedError

    def get(self, batch_id):
        raise NotImplementedError


class SqlAlchemyRepository:
    def __init__(self, session) -> None:
        self.session = session

    def add(self, batch: Batch):
        self.session.add(batch)

    def get(
        self,
        batch_id: Optional[str],
    ):
        return self.session.query(Batch).filter_by(reference=batch_id).first()

    def list(self):
        return self.session.query(Batch).all()


class ProductSQLRepository(AbstractRepository):

    def __init__(self, session) -> None:
        self.session = session
    
    def add(self, product: Product):
        self.session.add(product)
    
    def get(self, sku):
        return self.session.query(Product).filter_by(sku=sku).first()
    
    def list(self):
        return self.session.query(Product).all()
