from main import db
from .base import TimestampMixin


class QuestionModel(db.Model, TimestampMixin):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    expert_id = db.Column(db.Integer)
    text = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(1024), nullable=True)
    topic_id = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    messages = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(QuestionModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
