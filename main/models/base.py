from datetime import datetime

from main import db


class TimestampMixin(object):
    created = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


# Used to track modifications for the after_commit hook. See the comments on after_commit
class TrackChangesMixin:
    def reset_tracked_changes(self):
        self.__tracked_changes__ = set()

    def track_change(self, prop):
        self.__tracked_changes__.add(prop)

    def get_tracked_changes(self):
        return self.__tracked_changes__

    def initialize_tracked_changes(self):
        if not hasattr(self, '__tracked_changes__'):
            self.__tracked_changes__ = set()
