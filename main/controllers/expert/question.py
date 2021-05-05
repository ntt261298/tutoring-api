from marshmallow import fields

from main import app, auth, errors
from main.libs.validate_args import validate_args
from main.models.question import QuestionModel
from main.models.expert_state import ExpertStateModel
from main.schemas.base import BaseSchema
from main.enums import ExpertState
from main.engines.tasks.router import handle_bid, handle_skip, handle_question_done


class BidSchema(BaseSchema):
    question_id = fields.Integer(required=True)
    bid_amount = fields.Float(required=False)


@app.route('/expert/me/bids', methods=['POST'])
@auth.requires_token_auth('expert')
@validate_args(BidSchema())
def bid_question(expert, args):
    expert_state = ExpertStateModel.query.get(expert.id)
    if not expert_state:
        raise errors.BadRequest()
    if expert_state.state != ExpertState.BIDDING:
        raise errors.BadRequest()

    bid_amount = args.get('bid_amount')
    question_id = args.get('question_id')
    handle_bid.delay(expert.id, question_id, bid_amount)

    return BaseSchema().jsonify({})


class SkipSchema(BaseSchema):
    question_id = fields.Integer(required=True)


@app.route('/expert/me/skips', methods=['POST'])
@auth.requires_token_auth('expert')
@validate_args(SkipSchema())
def skip_question(expert, args):
    question = QuestionModel.query.get(args.get('question_id'))
    if not question:
        raise errors.BadRequest(message='Question is not found')
    handle_skip.delay(expert.id, question.id)

    return BaseSchema().jsonify({})


@app.route('/expert/me/questions/<int:question_id>', methods=['PUT'])
@auth.requires_token_auth('expert')
def update_expert_question(question_id, expert):
    # Check question existence
    question = QuestionModel.query.get(question_id)
    if not question:  # it should not happens, so given a generic error
        raise errors.BadRequest()

    # Check if it is current question expert working on
    if expert.expert_state.current_question_id != question.id:
        raise errors.BadRequest()

    # Check if expert is in working state
    if expert.expert_state.state != ExpertState.WORKING:
        raise errors.BadRequest()

    handle_question_done.delay(question_id)

    return BaseSchema().jsonify({})
