from flask import jsonify
from sqlalchemy import desc
from marshmallow import fields

from main import app, auth
from main.libs.validate_args import validate_args
from main.models.question import QuestionModel
from main.models.question_state import QuestionStateModel
from main.enums import QuestionState, Topic
from main.schemas.admin import PageSchema
from main.schemas.question import QuestionWithState


class SearchAdminQuestionSchema(PageSchema):
    items_per_page = fields.Integer(required=True)
    text = fields.String()
    topic_id = fields.Integer(required=True)
    user_ids = fields.String(required=True)
    expert_ids = fields.String(required=True)


@app.route('/admin/questions', methods=['GET'])
@auth.requires_token_auth('admin')
@validate_args(SearchAdminQuestionSchema())
def get_admin_questions(admin, args):
    filters = []

    query = QuestionModel.query. \
        join(QuestionModel.question_state). \
        join(QuestionModel.topic)

    if args['user_ids']:
        filters.append(QuestionModel.user_id.in_(args['user_ids'].split(',')))
    if args['expert_ids']:
        filters.append(QuestionModel.expert_id.in_(args['expert_ids'].split(',')))
    if args['text']:
        filters.append(QuestionModel.text.like('%' + args['text'] + '%'))
    if args['topic_id'] != Topic.ALL:
        filters.append(QuestionModel.topic_id == args['topic_id'])

    query = query.order_by(desc(QuestionModel.id))

    if filters:
        query = query.filter(*filters)

    print('query for questions', query)
    paging = query.paginate(args['page'], args['items_per_page'], False)
    questions = QuestionWithState(many=True).dump(paging.items)
    return jsonify({
        'questions': questions,
        'total_items': paging.total,
        'items_per_page': paging.per_page
    })


@app.route('/admin/active-questions', methods=['GET'])
@auth.requires_token_auth('admin')
def get_active_question(admin):
    question_states = QuestionStateModel.query.all()

    active_questions = 0
    for question_state in question_states:
        if question_state.state in QuestionState.get_active_states():
            active_questions += 1
    return jsonify({
        'active_questions': active_questions,
    })
