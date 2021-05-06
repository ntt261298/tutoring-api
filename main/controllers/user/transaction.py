from marshmallow import fields
from flask import jsonify

from main import app, auth
from main.libs.validate_args import validate_args
from main.schemas.base import BaseSchema
from main.schemas.admin import PageSchema
from main.models.transaction import TransactionModel


class SearchTransactionSchema(PageSchema):
    items_per_page = fields.Integer(required=True)


class TransactionSchema(BaseSchema):
    id = fields.String(required=True)
    package_name = fields.String(required=True)
    number_of_questions = fields.Integer(required=True)
    created = fields.String(required=True)
    amount = fields.String(required=True)


@app.route('/user/me/transactions', methods=['GET'])
@auth.requires_token_auth('user')
@validate_args(SearchTransactionSchema())
def get_user_transactions(user, args):
    query = TransactionModel.query.filter_by(
        user_id=user.id
    )

    paging = query.paginate(args['page'], args['items_per_page'], False)
    transactions = TransactionSchema(many=True).dump(paging.items)
    return jsonify({
        'transactions': transactions,
        'total_items': paging.total,
        'items_per_page': paging.per_page
    })
