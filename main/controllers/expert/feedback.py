from marshmallow import fields

from main import app, errors, auth
from main.models.feedback import FeedbackModel
from main.schemas.base import BaseSchema
from main.libs.validate_args import validate_args


class ExpertFeedbackSchema(BaseSchema):
    content = fields.String(required=True)


@app.route('/expert/feedback', methods=['POST'])
@auth.requires_token_auth('expert')
@validate_args(ExpertFeedbackSchema())
def create_expert_feedback(expert, args):
    # Create a new feedback
    feedback = FeedbackModel(
        expert_id=expert.id,
        content=args["content"],
    )
    try:
        feedback.save_to_db()
    except Exception:
        raise errors.BadRequest()

    return BaseSchema().jsonify({})
