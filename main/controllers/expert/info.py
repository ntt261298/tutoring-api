from marshmallow import fields

from main import app, errors, auth, db
from main.models.expert import ExpertModel
from main.schemas.base import BaseSchema
from main.schemas.expert import ExpertSchema
from main.libs.validate_args import validate_args
from main.libs import pw


@app.route('/expert/me/info', methods=['GET'])
@auth.requires_token_auth('expert')
def get_expert_info(expert):
    data = {
        "id": expert.id,
        "email": expert.email,
        "nickname": expert.nickname,
        "payment_method": expert.payment_method,
        "account_type": expert.account_type,
    }

    return ExpertSchema().jsonify(data)


class UpdateInfoSchema(BaseSchema):
    nickname = fields.String(missing=None)
    payment_method = fields.String(missing=None)


@app.route('/expert/me/info', methods=['PUT'])
@auth.requires_token_auth('expert')
@validate_args(UpdateInfoSchema())
def update_expert_info(expert, args):
    nickname = args.get('nickname')
    payment_method = args.get('payment_method')

    if nickname and len(nickname) < 6:
        raise errors.UserError(message=errors.UserErrors.NICKNAME_LENGTH_LIMIT)

    if nickname:
        # We do not allow two users to have the same nickname
        if ExpertModel.query.filter_by(nickname=nickname).first() is not None:
            raise errors.UserError(message=errors.UserErrors.UNAVAILABLE_NICKNAME)

        expert.nickname = nickname

    if payment_method:
        expert.payment_method = payment_method
    db.session.commit()

    return BaseSchema().jsonify({})


class ChangePasswordSchema(BaseSchema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True)


@app.route('/expert/me/password', methods=['PUT'])
@auth.requires_token_auth('expert')
@validate_args(ChangePasswordSchema())
def change_expert_password(expert, args):
    current_password = args.get('current_password')
    new_password = args.get('new_password')

    # Check if the user has a password
    if not expert.password_salt:
        raise errors.BadRequest()

    # Check if the current password match or not
    try:
        old_hash = pw.generate_hash(current_password, expert.password_salt)
    except ValueError:
        raise errors.UserError(
            message=errors.UserErrors.INVALID_CURRENT_PASSWORD)
    if expert.password_hash != old_hash:
        raise errors.UserError(
            message=errors.UserErrors.INVALID_CURRENT_PASSWORD)

    # Generate new password hash
    try:
        expert.password_hash = pw.generate_hash(new_password, expert.password_salt)
    except ValueError:
        raise errors.UserError(
            message=errors.UserErrors.PASSWORD_CONTAIN_SPECIAL_CHARACTERS)
    db.session.commit()
    return BaseSchema().jsonify({})
