from main import db
from main.models.question_state import QuestionStateModel
from .base import TimestampMixin


class QuestionModel(db.Model, TimestampMixin):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(1024), nullable=True)
    messages = db.Column(db.Text, nullable=False, default="")

    expert = db.relationship('ExpertModel', foreign_keys=[expert_id])
    user = db.relationship('UserModel', foreign_keys=[user_id])
    topic = db.relationship('TopicModel', foreign_keys=[topic_id])
    question_state = db.relationship('QuestionStateModel', back_populates='question', uselist=False)

    def __init__(self, *args, **kwargs):
        super(QuestionModel, self).__init__(*args, **kwargs)

        QuestionStateModel(
            question=self,
            topic_id=self.topic_id,
            user=self.user,
        )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
