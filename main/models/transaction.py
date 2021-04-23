from main import db
from .base import TimestampMixin


class TransactionModel(db.Model, TimestampMixin):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    package_name = db.String(128)
    package_type = db.String(128)
    amount = db.Column(db.Float)

    def __init__(self, *args, **kwargs):
        super(TransactionModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
