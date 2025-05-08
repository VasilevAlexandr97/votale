from sqlalchemy.orm import Session


class TransactionManager:
    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.rollback()
            print("rollback")
        else:
            self.commit()
            print("commit")

        self.close()
