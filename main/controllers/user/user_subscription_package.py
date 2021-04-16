from marshmallow import fields

from main import app, auth
from main.enums import SubscriptionStatus
from main.models.user_subscription_package import UserSubscriptionPackageModel
from main.schemas.base import BaseSchema


class UserSubscriptionPackageSchema(BaseSchema):
    id = fields.Integer(required=True)
    package_name = fields.String()
    package_type = fields.String()
    status = fields.String()
    type = fields.String()
    expired_in = fields.DateTime()


@app.route('/user/me/subscription_package', methods=['GET'])
@auth.requires_token_auth('user')
def get_user_subscription_package(user):
    user_subscription_package = UserSubscriptionPackageModel.query\
        .filter_by(user_id=user.id, status=SubscriptionStatus.ACTIVE)\
        .first()

    return UserSubscriptionPackageSchema().jsonify(user_subscription_package)
