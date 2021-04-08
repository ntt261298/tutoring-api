from main import db


class TransactionModel(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    package_id = db.Column(db.Integer, db.ForeignKey('subscription_package.id'))
    amount = db.Column(db.Float)

    def __init__(self, *args, **kwargs):
        super(TransactionModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
