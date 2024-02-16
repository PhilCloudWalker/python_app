from shop.model import Batch


class SqlAlchemyRepository:
    def __init__(self, session) -> None:
        self.session = session

    def add(self, batch: Batch):
        self.session.add(batch)

    def get(self, batch_id: str):
        return self.session.query(Batch).filter_by(reference=batch_id).first()

    def list(self):
        return self.session.query(Batch).all()