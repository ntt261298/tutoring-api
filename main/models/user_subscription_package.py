from main import db


class UserSubscriptionPackageModel(db.Model):
    __tablename__ = 'user_subscription_package_model'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    package_id = db.Column(db.Integer, db.ForeignKey('subscription_package.id'))
    expired_in = db.Column(db.DateTime)

    def __init__(self, *args, **kwargs):
        super(UserSubscriptionPackageModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
