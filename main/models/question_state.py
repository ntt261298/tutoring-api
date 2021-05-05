from main import db
from main.enums import QuestionState
from main.models.base import TimestampMixin, TrackChangesMixin


class QuestionStateModel(db.Model, TimestampMixin, TrackChangesMixin):
    __tablename__ = 'question_state'
    __track_changes__ = ['state', 'num_bidding']

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True, autoincrement=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    state = db.Column(db.String(15), nullable=False, default=QuestionState.NOT_ROUTED)
    topic_id = db.Column(db.Integer, nullable=False)
    # num_bidding stores how many experts are still actively bidding on the question
    num_bidding = db.Column(db.Integer, nullable=False, default=0)
    routing_expiration = db.Column(db.DateTime, nullable=True)
    chatting_expiration = db.Column(db.DateTime, nullable=True)
    # failed reason
    failed_reason = db.Column(db.String(100), nullable=True)

    user = db.relationship('UserModel', foreign_keys=[user_id])
    question = db.relationship('QuestionModel', back_populates='question_state', foreign_keys=[question_id])

    def __init__(self, *args, **kwargs):
        super(QuestionStateModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
