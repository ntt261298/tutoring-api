from marshmallow import fields
from flask import jsonify

from main import app, auth
from main.libs.validate_args import validate_args
from main.schemas.base import BaseSchema
from main.schemas.admin import PageSchema
from main.engines import admin as admin_engine


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


@app.route('/user/me/experts', methods=['GET'])
@auth.requires_token_auth('user')
@validate_args(SearchExpertSchema())
def get_user_experts(user, args):
    paging = admin_engine.search_experts(args)
    experts = AdminExpertSchema(many=True).dump(paging.items)
    return jsonify({
        'experts': experts,
        'total_items': paging.total,
        'items_per_page': paging.per_page
    })
