from main import db
from main.models.base import TimestampMixin


class QuestionMessageModel(db.Model, TimestampMixin):
    __tablename__ = 'question_message'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'))
    message = db.Column(db.Text, nullable=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)

    file = db.relationship('FileModel', foreign_keys=[file_id])
    user = db.relationship('UserModel', foreign_keys=[user_id])
    expert = db.relationship('ExpertModel', foreign_keys=[expert_id])
    question = db.relationship('QuestionModel', back_populates='messages', foreign_keys=[question_id])

    def __init__(self, *args, **kwargs):
        super(QuestionMessageModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
