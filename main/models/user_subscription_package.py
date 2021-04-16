from main import db


class UserSubscriptionPackageModel(db.Model):
    __tablename__ = 'user_subscription_package'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    package_name = db.Column(db.String(128))
    package_type = db.Column(db.String(128))
    amount = db.Column(db.Float)
    expired_in = db.Column(db.DateTime)
    number_of_questions = db.Column(db.Integer)
    status = db.Column(db.String(128))

    def __init__(self, *args, **kwargs):
        super(UserSubscriptionPackageModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
