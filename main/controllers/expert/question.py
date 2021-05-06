import base64
import json

from marshmallow import fields
from flask import request, jsonify

from main import app, auth, errors, db
from main.libs.validate_args import validate_args
from main.libs.validate_forms import validate_forms
from main.models.question import QuestionModel
from main.models.expert_state import ExpertStateModel
from main.models.question_message import QuestionMessageModel
from main.models.file import FileModel
from main.schemas.base import BaseSchema
from main.schemas.question import QuestionMessageSchema
from main.schemas.state import ResponseMessageSchema
from main.enums import ExpertState, QuestionState
from main.engines import pusher
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


@app.route('/expert/me/question_messages', methods=['POST'])
@auth.requires_token_auth('expert')
@validate_forms(QuestionMessageSchema())
def create_expert_question_message(expert, args):
    question = QuestionModel.query. \
        filter_by(id=args['question_id']). \
        one_or_none()

    if not question:
        raise errors.BadRequest()

    if question.question_state.state not in [QuestionState.WORKING]:
        raise errors.BadRequest()

    message = args['message']
    attached_file = request.files.get('file')
    # If the message doesn't contain either a file or some content, an error should be returned
    if attached_file is None and message is None:
        raise errors.BadRequest(message='Invalid input')

    question_message = QuestionMessageModel(
        question_id=question.id,
        expert_id=expert.id,
        message=message,
    )

    if attached_file:
        file_data = attached_file.read()
        rendered_data = base64.b64encode(file_data).decode('ascii')

        new_file = FileModel(name=attached_file.filename, rendered_data=rendered_data)
        new_file.save_to_db()
        question_message.file_id = new_file.id

    db.session.add(question_message)
    db.session.commit()

    print('question_message', question_message.file)
    response = ResponseMessageSchema().jsonify(question_message)
    response_dict = json.loads(response.get_data())

    pusher.trigger_message(args['question_id'], response_dict)

    return jsonify(response_dict)
