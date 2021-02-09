from main import db


class AskerRatingModel(db.Model):
    __tablename__ = 'asker_rating'

    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), primary_key=True, autoincrement=False)
    asker_id = db.Column(db.Integer, db.ForeignKey('asker.id'))
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(AskerRatingModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
