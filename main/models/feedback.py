from main import db
from .base import TimestampMixin


class FeedbackModel(db.Model, TimestampMixin):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    expert_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=True)
    content = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(FeedbackModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
