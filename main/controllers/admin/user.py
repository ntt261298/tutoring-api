from flask import jsonify
from marshmallow import fields

from main import app, auth, errors, db
from main.libs.validate_args import validate_args
from main.libs import pw
from main.models.user import UserModel
from main.schemas.base import BaseSchema
from main.schemas.admin import PageSchema
from main.engines import admin as admin_engine
from main.enums import AccountStatus


class SearchUserSchema(PageSchema):
    ids = fields.String(required=True)
    email = fields.String(required=True)
    page = fields.Integer(required=True)
    items_per_page = fields.Integer(required=True)


class AdminUserSchema(BaseSchema):
    id = fields.String(required=True)
    email = fields.String(required=True)
    created = fields.String(required=True)
    status = fields.String(required=True)


class CreateUserSchema(BaseSchema):
    email = fields.String(required=True)


class UpdateUserSchema(BaseSchema):
    free_balance = fields.Integer(required=True)


@app.route('/admin/users', methods=['GET'])
@auth.requires_token_auth('admin')
@validate_args(SearchUserSchema())
def get_admin_users(admin, args):
    paging = admin_engine.search_users(args)
    users = AdminUserSchema(many=True).dump(paging.items)
    return jsonify({
        'users': users,
        'total_items': paging.total,
        'items_per_page': paging.per_page
    })


@app.route('/admin/users', methods=['POST'])
@auth.requires_token_auth('admin')
@validate_args(CreateUserSchema())
def create_user(admin, args):
    if UserModel.query.filter_by(email=args['email']).first() is not None:
        raise errors.UserEmailAlreadyExistedError()

    password = pw.generate_temporary_password()
    password_salt, password_hash = pw.generate_password(password)

    user = UserModel(
        email=args['email'],
        password_salt=password_salt,
        password_hash=password_hash,
    )
    try:
        user.save_to_db()
    except Exception:
        raise errors.BadRequest()

    return jsonify({
        'email': args['email'],
        'password': password,
    })


@app.route('/admin/users/<int:user_id>', methods=['PUT'])
@auth.requires_token_auth('admin')
@validate_args(UpdateUserSchema())
def update_admin_user(admin, user_id, args):
    user = UserModel.query.get(user_id)
    if user is None:
        raise errors.BadRequest()

    user.free_credit_balance += args['free_balance']
    db.session.commit()

    return jsonify({})


@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@auth.requires_token_auth('admin')
def delete_admin_user(admin, user_id):
    user = UserModel.query.get(user_id)
    user.status = AccountStatus.DELETED
    db.session.commit()

    return jsonify({})


@app.route('/admin/users/<int:user_id>/undo-delete', methods=['PUT'])
@auth.requires_token_auth('admin')
def undo_delete_admin_user(admin, user_id):
    user = UserModel.query.get(user_id)
    user.status = AccountStatus.ACTIVE
    db.session.commit()

    return jsonify({})
