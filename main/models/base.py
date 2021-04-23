from datetime import datetime

from main import db


class TimestampMixin(object):
    created = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
