from main import db


class ExpertRankModel(db.Model):
    __tablename__ = 'expert_rank'

    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'), primary_key=True, autoincrement=False)
    topic_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    score_avg = db.Column(db.Float, nullable=False, default=0.0)

    def __init__(self, *args, **kwargs):
        super(ExpertRankModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
