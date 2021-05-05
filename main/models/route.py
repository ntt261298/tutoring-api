from main import db
from main.enums import RouteState
from main.models.base import TimestampMixin


class RouteModel(db.Model, TimestampMixin):
    __tablename__ = 'route'

    question_id = db.Column(db.Integer, db.ForeignKey('question_state.question_id'), primary_key=True, autoincrement=False)
    expert_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    state = db.Column(db.String(15), nullable=False, default=RouteState.BIDDING)
    bid_amount = db.Column(db.Float, nullable=True)
    # bidding scores
    grant_score = db.Column(db.Float, nullable=False, default=0)
    meta_data = db.Column(db.Text)

    question_state = db.relationship('QuestionStateModel', foreign_keys=[question_id])
    expert_state = db.relationship('ExpertStateModel', foreign_keys=[expert_id],
                                      primaryjoin='RouteModel.expert_id==ExpertStateModel.expert_id')

    def __init__(self, *args, **kwargs):
        super(RouteModel, self).__init__(*args, **kwargs)
