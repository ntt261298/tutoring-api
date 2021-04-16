from marshmallow import fields, Schema

from main import app, auth
from main.models.subscription_package import SubscriptionPackageModel
from main.schemas.base import BaseSchema


class SubscriptionPackagesSchema(BaseSchema):
    class SubscriptionPackageSchema(Schema):
        id = fields.Integer(required=True)
        name = fields.String()
        price = fields.Float()
        number_of_questions = fields.Integer(missing=0)
        type = fields.String()

    packages = fields.Nested(SubscriptionPackageSchema, many=True)


@app.route('/user/subscription_package', methods=['GET'])
@auth.requires_token_auth('user')
def get_subscription_package(user):
    subscription_packages = SubscriptionPackageModel.query.all()
    data = {
        "packages": subscription_packages
    }

    return SubscriptionPackagesSchema().jsonify(data)
