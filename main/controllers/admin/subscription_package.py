from flask import jsonify
from marshmallow import fields

from main import app, auth, db
from main.enums import SubscriptionType
from main.schemas.base import BaseSchema
from main.libs.validate_args import validate_args
from main.models.subscription_package import SubscriptionPackageModel


class AdminSubscriptionPackageSchema(BaseSchema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    price = fields.String(required=True)
    number_of_questions = fields.Integer(required=True)
    type = fields.String(required=True)


class UpdateSubscriptionPackageSchema(BaseSchema):
    name = fields.String(required=True)
    price = fields.String(required=True)
    number_of_questions = fields.Integer(required=False)


@app.route('/admin/subscription-packages', methods=['GET'])
@auth.requires_token_auth('admin')
def get_admin_subscription_packages(admin):
    subscription_packages = SubscriptionPackageModel.query.all()

    packages = AdminSubscriptionPackageSchema(many=True).dump(subscription_packages)
    return jsonify({
        'subscription_packages': packages,
    })


@app.route('/admin/subscription-packages/<int:subscription_package_id>', methods=['PUT'])
@validate_args(UpdateSubscriptionPackageSchema())
@auth.requires_token_auth('admin')
def update_admin_subscription_packages(admin, subscription_package_id, args):
    subscription_package = SubscriptionPackageModel.query.get(subscription_package_id)

    if args['name']:
        subscription_package.name = args['name']
    if args['price']:
        subscription_package.price = args['price']
    if args['number_of_questions'] and subscription_package.type == SubscriptionType.BUNDLE:
        subscription_package.number_of_questions = args['number_of_questions']

    db.session.commit()
    return jsonify({})
