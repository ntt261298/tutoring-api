import base64
import json

from flask import request, jsonify
from marshmallow import fields
from sqlalchemy import desc

from main import app, auth, errors, db
from main.enums import QuestionState, ReferenceFileType, Topic
from main.libs.validate_args import validate_args
from main.libs.validate_forms import validate_forms
from main.schemas.question import CreateQuestionSchema, QuestionSchema, QuestionWithState, QuestionMessageSchema
from main.models.question import QuestionModel
from main.models.question_state import QuestionStateModel
from main.models.topic import TopicModel
from main.models.file import FileModel
from main.models.question_message import QuestionMessageModel
from main.schemas.admin import PageSchema
from main.engines import pusher


def _check_user_has_active_question(user):
    """
    Check if user has active question
    :param user: User to check
    """
    if user.current_question_id:
        question_state = QuestionStateModel.query.get(user.current_question_id)
        # Prevent user from posting another problem if the rating was not completed
        if question_state and question_state.state not in QuestionState.get_finished_states():
            raise errors.QuestionAlreadyExists()


@app.route('/user/me/questions', methods=['POST'])
@auth.requires_token_auth('user')
@validate_forms(CreateQuestionSchema())
def create_question(user, args):
    # Make sure user doesn't have active problem
    _check_user_has_active_question(user)

    # Validate topic
    topic_id = args.get('topic_id')
    topic = TopicModel.query.get(topic_id)
    if topic is None:
        raise errors.BadRequest(message='Topic does not exist')

    attached_file = request.files.get('file')

    new_file = None
    # Create file from user's uploaded file. It is an image (.jpeg, .jpg, .png)
    if attached_file:
        file_data = attached_file.read()
        rendered_data = base64.b64encode(file_data).decode('ascii')

        new_file = FileModel(name=attached_file.filename, rendered_data=rendered_data)
        new_file.save_to_db()

    # Create question
    question = QuestionModel(
        user=user,
        topic_id=topic_id,
        text=args.get('content'),
    )
    if new_file:
        question.file_id = new_file.id
    question.save_to_db()

    # Update reference_id in FileModel objects
    db.session.flush()
    if new_file:
        new_file.reference_id = question.id
        new_file.reference_type = ReferenceFileType.QUESTION_DESCRIPTION

    user.current_question = question
    db.session.commit()

    return QuestionSchema().jsonify(question)


@app.route('/user/me/questions/<int:question_id>', methods=['GET'])
@auth.requires_token_auth('user')
def get_user_question(user, question_id):
    """
    Get detailed question of user with messages
    """
    question = QuestionModel.query. \
        filter(QuestionModel.user_id == user.id). \
        filter(QuestionModel.id == question_id). \
        join(QuestionModel.question_state). \
        join(QuestionModel.topic). \
        one_or_none()

    if question is None:
        raise errors.BadRequest()

    return QuestionWithState().jsonify(question, many=False)


class SearchQuestionSchema(PageSchema):
    items_per_page = fields.Integer(required=True)
    text = fields.String()
    topic_id = fields.Integer(required=True)


@app.route('/user/me/questions', methods=['GET'])
@auth.requires_token_auth('user')
@validate_args(SearchQuestionSchema())
def get_user_questions(user, args):
    filters = []

    query = QuestionModel.query. \
        filter(QuestionModel.user_id == user.id). \
        join(QuestionModel.question_state). \
        filter(QuestionStateModel.state == QuestionState.COMPLETE).\
        join(QuestionModel.topic). \
        join(QuestionModel.user_rating)

    if args['text']:
        filters.append(QuestionModel.text.like('%' + args['text'] + '%'))
    if args['topic_id'] != Topic.ALL:
        filters.append(QuestionModel.topic_id == args['topic_id'])

    query = query.order_by(desc(QuestionModel.id))

    if filters:
        query = query.filter(*filters)

    paging = query.paginate(args['page'], args['items_per_page'], False)
    questions = QuestionWithState(many=True).dump(paging.items)
    return jsonify({
        'questions': questions,
        'total_items': paging.total,
        'items_per_page': paging.per_page
    })


@app.route('/user/me/question_messages', methods=['POST'])
@auth.requires_token_auth('user')
@validate_forms(QuestionMessageSchema())
def create_user_question_message(user, args):
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
        user_id=user.id,
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

    response = QuestionMessageSchema().jsonify(question_message)
    response_dict = json.loads(response.get_data())

    if attached_file:
        response_dict['message_type'] = 'file'
    else:
        response_dict['message_type'] = 'text'

    pusher.trigger_message(args['question_id'], response_dict)

    return jsonify(response_dict)
