from main import db
from main.libs.jwttoken import generate_access_token_nonce


class ExpertModel(db.Model):
    __tablename__ = 'expert'
    account_type = 'expert'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(64), nullable=True)
    password_salt = db.Column(db.String(64), nullable=True)
    access_token_nonce = db.Column(db.String(8), nullable=False, default=generate_access_token_nonce)
    first_name = db.Column(db.String(32), nullable=True)
    last_name = db.Column(db.String(32), nullable=True)
    email_verified = db.Column(db.Boolean(create_constraint=False), nullable=False, default=False)
    browser_fingerprint = db.Column(db.String(255))
    google_id = db.Column(db.String(64))
    is_fraud = db.Column(db.Boolean(create_constraint=False), nullable=False, default=False)

    expert_topics = db.relationship('ExpertTopicModel')
    expert_ranks = db.relationship('ExpertRankModel')

    def __init__(self, *args, **kwargs):
        super(ExpertModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
