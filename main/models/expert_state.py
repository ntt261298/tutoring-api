from main import db
from main.enums import ExpertState
from .base import TimestampMixin


class ExpertStateModel(db.Model, TimestampMixin):
    __tablename__ = 'expert_state'

    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'), primary_key=True, autoincrement=False)
    state = db.Column(db.String(15), nullable=False, default=ExpertState.NOT_ROUTED)
    connected = db.Column(db.Boolean(create_constraint=False), nullable=False, default=False)
    current_question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    current_question = db.relationship('QuestionModel', foreign_keys=[current_question_id])
    expert = db.relationship('ExpertModel', back_populates='expert_state', foreign_keys=[expert_id])
    expert_topics = db.relationship(
        'ExpertTopicModel',
        primaryjoin='ExpertStateModel.expert_id == ExpertTopicModel.expert_id',
        foreign_keys='ExpertTopicModel.expert_id'
    )
    expert_ranks = db.relationship(
        'ExpertRankModel',
        primaryjoin='ExpertStateModel.expert_id == ExpertRankModel.expert_id',
        foreign_keys='ExpertRankModel.expert_id'
    )

    def __init__(self, *args, **kwargs):
        super(ExpertStateModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
