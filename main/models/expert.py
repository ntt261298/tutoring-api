from main import db
from .base import TimestampMixin
from main.libs.jwttoken import generate_access_token_nonce


class ExpertModel(db.Model, TimestampMixin):
    __tablename__ = 'expert'
    account_type = 'expert'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(64), nullable=True)
    password_salt = db.Column(db.String(64), nullable=True)
    access_token_nonce = db.Column(db.String(8), nullable=False, default=generate_access_token_nonce)
    nickname = db.Column(db.String(128), nullable=True)
    email_verified = db.Column(db.Boolean(create_constraint=False), nullable=False, default=False)
    browser_fingerprint = db.Column(db.String(255))
    is_fraud = db.Column(db.Boolean(create_constraint=False), nullable=False, default=False)
    status = db.Column(db.String(64), nullable=False, default="active")
    payment_method = db.Column(db.String(255))

    expert_topics = db.relationship('ExpertTopicModel')
    expert_ranks = db.relationship('ExpertRankModel')

    def __init__(self, *args, **kwargs):
        super(ExpertModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
