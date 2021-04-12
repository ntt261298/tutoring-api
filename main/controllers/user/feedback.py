from marshmallow import fields

from main import app, errors, auth
from main.models.feedback import FeedbackModel
from main.schemas.base import BaseSchema
from main.libs.validate_args import validate_args


class UserFeedbackSchema(BaseSchema):
    content = fields.String(required=True)


@app.route('/user/feedback', methods=['POST'])
@auth.requires_token_auth('user')
@validate_args(UserFeedbackSchema())
def create_feedback(user, args):
    # Create a new feedback
    feedback = FeedbackModel(
        user_id=user.id,
        content=args["content"],
    )
    try:
        feedback.save_to_db()
    except Exception:
        raise errors.BadRequest()

    return BaseSchema().jsonify({})
