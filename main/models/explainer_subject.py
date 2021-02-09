from main import db


class ExplainerSubject(db.Model):
    __tablename__ = 'explainer_subject'

    explainer_id = db.Column(db.Integer, db.ForeignKey('explainer.id'), primary_key=True, autoincrement=False)
    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=False)

    def __init__(self, *args, **kwargs):
        super(ExplainerSubject, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
