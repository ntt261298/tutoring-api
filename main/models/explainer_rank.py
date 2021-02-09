from main import db


class ExplainerRank(db.Model):
    __tablename__ = 'explainer_rank'

    explainer_id = db.Column(db.Integer, db.ForeignKey('explainer.id'), primary_key=True, autoincrement=False)
    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    score_avg = db.Column(db.Float, nullable=False, default=0.0)

    def __init__(self, *args, **kwargs):
        super(ExplainerRank, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
