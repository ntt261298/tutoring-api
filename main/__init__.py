import pusher
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SignallingSession
from sqlalchemy.event import listen
from sqlalchemy import inspect

from config import config
from main.libs.make_celery import make_celery

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)

CORS(app)

pusher_client = pusher.Pusher(
    app_id=config.PUSHER_APP_ID,
    key=config.PUSHER_KEY,
    secret=config.PUSHER_SECRET,
    cluster=config.PUSHER_CLUSTER
)

celery = make_celery(app)
app.app_context().push()

from main.models import *
import main.controllers
import main.errors


# This is part of an after_commit hook to track
# which models have changed in this commit,
# but only after the transaction has actually executed.
# Only models that use the TrackChangesMixin are used and
# they must have an array called __track_changes__
# that lists which properties to track.
# The hook will get called if any part of the model changes,
# but only the tracked changes will have the history
# of whether or not they were changed
def _on_model_committed(model_instance):
    from main.models.question_state import QuestionStateModel
    from main.models.expert_state import ExpertStateModel

    from main import router, pusher_hooks
    from main.engines.pusher import trigger_state_change

    if isinstance(model_instance, QuestionStateModel):
        router.on_question_state_commit(model_instance)
        pusher_hooks.on_question_state_commit(model_instance)
    elif isinstance(model_instance, ExpertStateModel):
        pusher_hooks.on_expert_state_commit(model_instance)


def _after_commit_handler(session):
    if hasattr(session, '_tracked_models'):
        for model in session._tracked_models:
            _on_model_committed(model)
            model.reset_tracked_changes()
        session._tracked_models.clear()


def _after_rollback_handler(session):
    if hasattr(session, '_tracked_models'):
        for (model, operation) in session._tracked_models:
            model.reset_tracked_changes()
        session._tracked_models.clear()


def _after_flush_handler(session, flush_ctx):
    if not hasattr(session, '_tracked_models'):
        session._tracked_models = set()
    for obj in session.dirty:
        if getattr(obj, 'track_change', None):
            obj.initialize_tracked_changes()
            session._tracked_models.add(obj)
            for prop in obj.__track_changes__:
                if inspect(obj).attrs[prop].history.has_changes():
                    obj.track_change(prop)
    for obj in session.new:
        if getattr(obj, 'track_change', None):
            session._tracked_models.add(obj)
            obj.initialize_tracked_changes()
            for prop in obj.__track_changes__:
                obj.track_change(prop)


listen(SignallingSession, 'after_commit', _after_commit_handler)
listen(SignallingSession, 'after_flush', _after_flush_handler)
listen(SignallingSession, 'after_rollback', _after_rollback_handler)


from main.engines.tasks.daily import terminate_subscription, pay_for_experts, \
    TERMINATE_SUBSCRIPTION_PERIOD, PAY_FOR_EXPERTS_PERIOD

terminate_subscription.s().apply_async(countdown=TERMINATE_SUBSCRIPTION_PERIOD)
pay_for_experts.s().apply_async(countdown=PAY_FOR_EXPERTS_PERIOD)
