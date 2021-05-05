from main import db
from .base import TimestampMixin


class FileModel(db.Model, TimestampMixin):
    __tablename__ = 'file'

    id = db.Column(db.Integer,  primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    rendered_data = db.Column(db.Text(4294000000), nullable=False)
    reference_id = db.Column(db.Integer, nullable=True)
    reference_type = db.Column(db.String(30), nullable=True)

    def __init__(self, *args, **kwargs):
        super(FileModel, self).__init__(*args, **kwargs)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
