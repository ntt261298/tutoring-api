from main import db
from .base import TimestampMixin
from main.libs.jwttoken import generate_access_token_nonce


class AdminModel(db.Model, TimestampMixin):
    __tablename__ = 'admin'
    account_type = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    google_id = db.Column(db.String(64))
    access_token_nonce = db.Column(db.String(8), nullable=False, default=generate_access_token_nonce)
    google_name = db.Column(db.Unicode(128), nullable=True)

    def __init__(self, *args, **kwargs):
        super(AdminModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
