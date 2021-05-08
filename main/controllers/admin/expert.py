from flask import jsonify
from marshmallow import fields

from main import app, auth, errors, db
from main.libs.validate_args import validate_args
from main.libs import pw
from main.models.expert import ExpertModel
from main.models.expert_state import ExpertStateModel
from main.models.expert_topic import ExpertTopicModel
from main.models.expert_rank import ExpertRankModel
from main.schemas.base import BaseSchema
from main.schemas.admin import PageSchema
from main.engines import admin as admin_engine
from main.enums import Topic, AccountStatus


class SearchExpertSchema(PageSchema):
    ids = fields.String(required=True)
    email = fields.String(required=True)
    topic_id = fields.Integer(required=True)
    page = fields.Integer(required=True)
    items_per_page = fields.Integer(required=True)


class ExpertTopicSchema(BaseSchema):
    expert_id = fields.Integer(required=True)
    topic_id = fields.Integer(required=True)


class ExpertRankSchema(BaseSchema):
    expert_id = fields.Integer(required=True)
    topic_id = fields.Integer(required=True)
    score_avg = fields.Float(required=True)


class AdminExpertSchema(BaseSchema):
    id = fields.String(required=True)
    email = fields.String(required=True)
    expert_topics = fields.Nested(ExpertTopicSchema, many=True)
    expert_ranks = fields.Nested(ExpertRankSchema, many=True)
    created = fields.String(required=True)
    status = fields.String(required=True)


class TopicSchema(BaseSchema):
    math = fields.Boolean()
    english = fields.Boolean()


class CreateExpertSchema(BaseSchema):
    email = fields.String(required=True)
    topic = fields.Nested(TopicSchema())
    math_ranking = fields.Float(allow_none=True)
    english_ranking = fields.Float(allow_none=True)


class UpdateExpertSchema(BaseSchema):
    topic = fields.Nested(TopicSchema())
    math_ranking = fields.Float(allow_none=True)
    english_ranking = fields.Float(allow_none=True)


@app.route('/admin/experts', methods=['GET'])
@auth.requires_token_auth('admin')
@validate_args(SearchExpertSchema())
def get_admin_experts(admin, args):
    paging = admin_engine.search_experts(args)
    experts = AdminExpertSchema(many=True).dump(paging.items)
    return jsonify({
        'experts': experts,
        'total_items': paging.total,
        'items_per_page': paging.per_page
    })


@app.route('/admin/active-experts', methods=['GET'])
@auth.requires_token_auth('admin')
def get_active_experts(admin):
    expert_states = ExpertStateModel.query.all()

    active_experts = 0
    for expert_state in expert_states:
        if expert_state.connected is True:
            print('expert_state.connected', expert_state.connected)
            active_experts += 1

    return jsonify({
        'active_experts': active_experts,
    })


@app.route('/admin/experts', methods=['POST'])
@auth.requires_token_auth('admin')
@validate_args(CreateExpertSchema())
def create_expert(admin, args):
    if ExpertModel.query.filter_by(email=args['email']).first() is not None:
        raise errors.UserEmailAlreadyExistedError()

    password = pw.generate_temporary_password()
    password_salt, password_hash = pw.generate_password(password)

    expert = ExpertModel(
        email=args['email'],
        password_salt=password_salt,
        password_hash=password_hash,
    )
    try:
        expert.save_to_db()
    except Exception:
        raise errors.BadRequest()

    created_expert = ExpertModel.query.filter_by(email=args['email']).first()

    if args['topic'].get('math'):
        expert_topic = ExpertTopicModel(
            expert_id=created_expert.id,
            topic_id=Topic.MATH,
        )
        expert_topic.save_to_db()

        expert_ranking = ExpertRankModel(
            expert_id=created_expert.id,
            topic_id=Topic.MATH,
            initial_score=args['math_ranking'],
            score_avg=args['math_ranking'],
        )
        expert_ranking.save_to_db()

    if args['topic'].get('english'):
        expert_topic = ExpertTopicModel(
            expert_id=created_expert.id,
            topic_id=Topic.ENGLISH,
        )
        expert_topic.save_to_db()
        expert_ranking = ExpertRankModel(
            expert_id=created_expert.id,
            topic_id=Topic.ENGLISH,
            initial_score=args['english_ranking'],
            score_avg=args['english_ranking'],
        )
        expert_ranking.save_to_db()

    return jsonify({
        'email': args['email'],
        'password': password,
    })


@app.route('/admin/experts/<int:expert_id>', methods=['PUT'])
@auth.requires_token_auth('admin')
@validate_args(UpdateExpertSchema())
def update_admin_expert(admin, expert_id, args):
    expert = ExpertModel.query.get(expert_id)
    if expert is None:
        raise errors.BadRequest()

    experts = ExpertTopicModel.query\
        .with_entities(ExpertTopicModel.topic_id)\
        .filter_by(expert_id=expert.id).all()

    expert_topics = []
    for _expert in experts:
        expert_topics.append(_expert.topic_id)

    # Add math topic
    if args['topic'].get('math') and Topic.MATH not in expert_topics:
        expert_topic = ExpertTopicModel(
            expert_id=expert.id,
            topic_id=Topic.MATH,
        )
        expert_topic.save_to_db()

        expert_ranking = ExpertRankModel(
            expert_id=expert.id,
            topic_id=Topic.MATH,
            initial_score=args['math_ranking'],
            score_avg=args['math_ranking'],
        )
        expert_ranking.save_to_db()

    # Add english topic
    if args['topic'].get('english') and Topic.ENGLISH not in expert_topics:
        expert_topic = ExpertTopicModel(
            expert_id=expert.id,
            topic_id=Topic.ENGLISH,
        )
        expert_topic.save_to_db()
        expert_ranking = ExpertRankModel(
            expert_id=expert.id,
            topic_id=Topic.ENGLISH,
            initial_score=args['english_ranking'],
            score_avg=args['english_ranking'],
        )
        expert_ranking.save_to_db()

    # Remove math topic
    if not args['topic'].get('math') and Topic.MATH in expert_topics:
        admin_engine.delete_expert_topic(expert.id, Topic.MATH)

    # Remove english topic
    if not args['topic'].get('english') and Topic.ENGLISH in expert_topics:
        admin_engine.delete_expert_topic(expert.id, Topic.ENGLISH)

    return jsonify({})


@app.route('/admin/experts/<int:expert_id>', methods=['DELETE'])
@auth.requires_token_auth('admin')
def delete_admin_expert(admin, expert_id):
    expert = ExpertModel.query.get(expert_id)
    expert.status = AccountStatus.DELETED
    db.session.commit()

    return jsonify({})


@app.route('/admin/experts/<int:expert_id>/undo-delete', methods=['PUT'])
@auth.requires_token_auth('admin')
def undo_delete_admin_expert(admin, expert_id):
    expert = ExpertModel.query.get(expert_id)
    expert.status = AccountStatus.ACTIVE
    db.session.commit()

    return jsonify({})
