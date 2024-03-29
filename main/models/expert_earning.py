from main import db
from .base import TimestampMixin


class ExpertEarningModel(db.Model, TimestampMixin):
    __tablename__ = 'expert_earning'

    id = db.Column(db.Integer, primary_key=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(64), nullable=False, default='unpaid')

    question = db.relationship('QuestionModel', foreign_keys=[question_id])
    expert = db.relationship('ExpertModel', back_populates='expert_earnings', foreign_keys=[expert_id])

    def __init__(self, *args, **kwargs):
        super(ExpertEarningModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
