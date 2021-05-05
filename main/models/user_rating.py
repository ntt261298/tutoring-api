from main import db
from .base import TimestampMixin


class UserRatingModel(db.Model, TimestampMixin):
    __tablename__ = 'user_rating'

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True, autoincrement=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(UserRatingModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
