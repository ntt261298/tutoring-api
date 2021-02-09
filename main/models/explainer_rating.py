from main import db


class ExplainerRatingModel(db.Model):
    __tablename__ = 'explainer_rating'

    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), primary_key=True, autoincrement=False)
    explainer_id = db.Column(db.Integer, db.ForeignKey('explainer.id'))
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(ExplainerRatingModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
