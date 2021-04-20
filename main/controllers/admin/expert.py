from flask import jsonify
from marshmallow import fields

from main import app, auth, errors
from main.libs.validate_args import validate_args
from main.libs import pw
from main.models.expert import ExpertModel
from main.models.expert_topic import ExpertTopicModel
from main.schemas.base import BaseSchema
from main.schemas.admin import PageSchema
from main.engines import admin as admin_engine
from main.enums import Topic


class SearchExpertSchema(PageSchema):
    ids = fields.String(required=True)
    email = fields.String(required=True)
    topic_id = fields.Integer(required=True)
    page = fields.Integer(required=True)
    items_per_page = fields.Integer(required=True)


class AdminExpertSchema(BaseSchema):
    id = fields.String(required=True)
    email = fields.String(required=True)
    rating = fields.Integer(required=True)
    signup_date = fields.String(required=True)


class TopicSchema(BaseSchema):
    math = fields.Boolean()
    english = fields.Boolean()


class CreateExpertSchema(BaseSchema):
    email = fields.String(required=True)
    topic = fields.Nested(TopicSchema())


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

    if args['topic'].get('english'):
        expert_topic = ExpertTopicModel(
            expert_id=created_expert.id,
            topic_id=Topic.ENGLISH,
        )
        expert_topic.save_to_db()

    return jsonify({
        'email': args['email'],
        'password': password,
    })
