from marshmallow import fields
from flask import jsonify

from main import app, auth
from main.libs.validate_args import validate_args
from main.schemas.base import BaseSchema
from main.schemas.admin import PageSchema
from main.models.expert_earning import ExpertEarningModel


class SearchEarningSchema(PageSchema):
    items_per_page = fields.Integer(required=True)


class QuestionSchema(BaseSchema):
    id = fields.String(required=True)
    text = fields.String(required=True)


class EarningSchema(BaseSchema):
    id = fields.String(required=True)
    created = fields.String(required=True)
    amount = fields.Float(required=True)
    status = fields.String(required=True)
    question = fields.Nested(QuestionSchema)


@app.route('/expert/me/earnings', methods=['GET'])
@auth.requires_token_auth('expert')
@validate_args(SearchEarningSchema())
def get_user_earnings(expert, args):
    query = ExpertEarningModel.query.filter_by(
        expert_id=expert.id
    )

    paging = query.paginate(args['page'], args['items_per_page'], False)
    earnings = EarningSchema(many=True).dump(paging.items)
    return jsonify({
        'earnings': earnings,
        'total_items': paging.total,
        'items_per_page': paging.per_page
    })
