from flask import jsonify
from marshmallow import fields

from main import app, auth
from main.libs.validate_args import validate_args
from main.schemas.base import BaseSchema
from main.schemas.admin import PageSchema
from main.engines import admin as admin_engine
from main.enums import AccountType


class SearchFeedbackSchema(PageSchema):
    email = fields.String(required=True)
    content = fields.String(required=True)
    account_type = fields.String(required=True)
    page = fields.Integer(required=True)
    items_per_page = fields.Integer(required=True)


class AdminFeedbackSchema(BaseSchema):
    id = fields.String(required=True)
    created = fields.String(required=True)
    email = fields.String(required=True)
    content = fields.String(required=True)


@app.route('/admin/feedback', methods=['GET'])
@auth.requires_token_auth('admin')
@validate_args(SearchFeedbackSchema())
def get_admin_feedback(admin, args):
    paging = admin_engine.search_feedback(args)
    result = []
    if args['account_type'] == AccountType.USER:
        for item in paging.items:
            (user, feedback) = item
            result.append({
                "id": feedback.id,
                "created": feedback.created,
                "email": user.email,
                "content": feedback.content,
            })

    if args['account_type'] == AccountType.EXPERT:
        for item in paging.items:
            (expert, feedback) = item
            result.append({
                "id": feedback.id,
                "created": feedback.created,
                "email": expert.email,
                "content": feedback.content,
            })

    feedback = AdminFeedbackSchema(many=True).dump(result)
    return jsonify({
        'feedback': feedback,
        'total_items': paging.total,
        'items_per_page': paging.per_page
    })
