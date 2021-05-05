import base64

from flask import request

from main import app, auth, errors, db
from main.enums import QuestionState, ReferenceFileType
from main.libs.validate_forms import validate_forms
from main.schemas.question import CreateQuestionSchema, QuestionSchema, QuestionWithState
from main.models.question import QuestionModel
from main.models.expert import ExpertModel
from main.models.question_state import QuestionStateModel
from main.models.topic import TopicModel
from main.models.file import FileModel


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
    print('attached_file', attached_file)
    # Create file from user's uploaded file. It is an image (.jpeg, .jpg, .png)
    if attached_file:
        file_data = attached_file.read()
        rendered_data = base64.b64encode(file_data).decode('ascii')

        new_file = FileModel(name=attached_file.filename, rendered_data=rendered_data)
        new_file.save_to_db()

    print('new_file', new_file)

    # Create question
    question = QuestionModel(
        user=user,
        topic_id=topic_id,
        text=args.get('content'),
    )
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
