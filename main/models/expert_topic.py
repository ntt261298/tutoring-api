from main import db
from .base import TimestampMixin


class ExpertTopicModel(db.Model, TimestampMixin):
    __tablename__ = 'expert_topic'

    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'), primary_key=True, autoincrement=False)
    topic_id = db.Column(db.Integer, primary_key=True, autoincrement=False)

    def __init__(self, *args, **kwargs):
        super(ExpertTopicModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
