from flask import jsonify
from marshmallow import fields

from main import app, auth
from main.schemas.base import BaseSchema
from main.models.transaction import TransactionModel


class AdminTransactionSchema(BaseSchema):
    user_id = fields.Integer(required=True)
    amount = fields.Integer(required=True)
    package_name = fields.String(required=True)
    number_of_questions = fields.Integer(required=True)


@app.route('/admin/transactions', methods=['GET'])
@auth.requires_token_auth('admin')
def get_admin_transactions(admin):
    transactions = TransactionModel.query.all()

    result = AdminTransactionSchema(many=True).dump(transactions)
    return jsonify({
        'transactions': result,
    })
