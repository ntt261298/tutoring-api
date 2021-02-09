from main import db


class ProblemModel(db.Model):
    __tablename__ = 'problem'

    id = db.Column(db.Integer, primary_key=True)
    asker_id = db.Column(db.Integer, db.ForeignKey('asker.id'), nullable=False)
    explainer_id = db.Column(db.Integer, db.ForeignKey('explainer.id'))
    text = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(1024), nullable=True)
    subject_id = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False)

    def __init__(self, *args, **kwargs):
        super(ProblemModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
