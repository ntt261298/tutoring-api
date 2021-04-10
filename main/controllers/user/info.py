from marshmallow import fields

from main import app, errors, auth, db
from main.models.user import UserModel
from main.schemas.base import BaseSchema
from main.schemas.user import UserSchema
from main.libs.validate_args import validate_args
from main.libs import pw


@app.route('/user/me/info', methods=['GET'])
@auth.requires_token_auth('user')
def get_user_info(user):
    data = {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "free_credit_balance": user.free_credit_balance,
        "paid_credit_balance": user.paid_credit_balance
    }

    return UserSchema().jsonify(data)


class UpdateInfoSchema(BaseSchema):
    nickname = fields.String(missing=None)


@app.route('/user/me/info', methods=['PUT'])
@auth.requires_token_auth('user')
@validate_args(UpdateInfoSchema())
def update_user_info(user, args):
    nickname = args.get('nickname')
    if len(nickname) < 6:
        raise errors.UserError(message=errors.UserErrors.NICKNAME_LENGTH_LIMIT)
    # We do not allow two users to have the same nickname
    if UserModel.query.filter_by(nickname=nickname).first() is not None:
        raise errors.UserError(message=errors.UserErrors.UNAVAILABLE_NICKNAME)

    user.nickname = nickname
    db.session.commit()

    return BaseSchema().jsonify({})


class ChangePasswordSchema(BaseSchema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True)


@app.route('/user/me/password', methods=['PUT'])
@auth.requires_token_auth('user')
@validate_args(ChangePasswordSchema())
def change_password(user, args):
    current_password = args.get('current_password')
    new_password = args.get('new_password')

    # Check if the user has a password
    if not user.password_salt:
        raise errors.BadRequest()

    # Check if the current password match or not
    try:
        old_hash = pw.generate_hash(current_password, user.password_salt)
    except ValueError:
        raise errors.UserError(
            message=errors.UserErrors.INVALID_CURRENT_PASSWORD)
    if user.password_hash != old_hash:
        raise errors.UserError(
            message=errors.UserErrors.INVALID_CURRENT_PASSWORD)

    # Generate new password hash
    try:
        user.password_hash = pw.generate_hash(new_password, user.password_salt)
    except ValueError:
        raise errors.UserError(
            message=errors.UserErrors.PASSWORD_CONTAIN_SPECIAL_CHARACTERS)
    db.session.commit()
    return BaseSchema().jsonify({})
