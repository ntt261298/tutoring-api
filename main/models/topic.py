from main import db
from .base import TimestampMixin


class TopicModel(db.Model, TimestampMixin):
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    def __init__(self, *args, **kwargs):
        super(TopicModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
