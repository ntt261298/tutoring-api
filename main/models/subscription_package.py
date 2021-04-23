from main import db
from .base import TimestampMixin


class SubscriptionPackageModel(db.Model, TimestampMixin):
    __tablename__ = 'subscription_package'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    number_of_questions = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(256), nullable=False)

    def __init__(self, *args, **kwargs):
        super(SubscriptionPackageModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
