from main import db
from main.libs.jwttoken import generate_access_token_nonce


class UserModel(db.Model):
    __tablename__ = 'user'
    account_type = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(64), nullable=True)
    password_salt = db.Column(db.String(64), nullable=True)
    access_token_nonce = db.Column(db.String(8), nullable=False, default=generate_access_token_nonce)
    nickname = db.Column(db.String(64), nullable=True)
    free_credit_balance = db.Column(db.Integer, nullable=False, default=0)
    paid_credit_balance = db.Column(db.Integer, nullable=False, default=0)
    current_question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    browser_fingerprint = db.Column(db.String(255))
    google_id = db.Column(db.String(64))
    payment_methods = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(UserModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
