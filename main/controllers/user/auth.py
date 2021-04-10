from marshmallow import fields, validate
from google_auth_oauthlib.flow import Flow

from config import config
from main import app
from main.models.user import UserModel
from main.schemas.base import BaseSchema
from main.schemas.user import AccessTokenSchema
from main.libs.validate_args import validate_args
from main.libs import pw, jwttoken
from main import errors


class UserLoginSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserSignupSchema(BaseSchema):
    email = fields.Email(required=False, missing=None)
    password = fields.String(required=False, missing=None)
    browser_fingerprint = fields.String(required=False, missing=None)
    nickname = fields.String(required=False, missing=None, validate=validate.Length(min=1))


class GoogleAuthSchema(BaseSchema):
    authorization_code = fields.String(required=True)


@app.route('/log-in/user/email', methods=['POST'])
@validate_args(UserLoginSchema())
def log_in_user_email(args):
    user = UserModel.query. \
        filter_by(email=args['email']). \
        one_or_none()
    if not user:
        raise errors.AccountNotExisted()
        # Check if the password is correct
    if not user.password_hash or not user.password_salt:
        raise errors.EmailAndPasswordNotMatch()
    try:
        if user.password_hash != pw.generate_hash(args['password'], user.password_salt):
            raise errors.EmailAndPasswordNotMatch()
    except ValueError:
        raise errors.EmailAndPasswordNotMatch()

    return AccessTokenSchema().jsonify({
        'access_token': jwttoken.encode(user),
        'account_id': user.id,
        'name': user.nickname,
        'is_signup': False,
        'email': user.email,
    })


@app.route('/sign-up/user/email', methods=['POST'])
@validate_args(UserSignupSchema())
def sign_up_user_email(args):
    email = args.get('email')
    password = args.get('password')
    browser_fingerprint = args.get('browser_fingerprint')
    nickname = args.get('nickname')

    # Check the existence of the account
    if UserModel.query.filter_by(email=email).first() is not None:
        raise errors.UserEmailAlreadyExistedError()

    # Generate password hash and salt
    if not password:
        password = pw.generate_temporary_password()
    password_salt, password_hash = pw.generate_password(password)

    # Create a new user
    user = UserModel(
        email=email,
        password_hash=password_hash,
        password_salt=password_salt,
        nickname=nickname,
        browser_fingerprint=browser_fingerprint,
    )
    try:
        user.save_to_db()
    except Exception:
        raise errors.BadRequest()

    return AccessTokenSchema().jsonify({
        'access_token': jwttoken.encode(user),
        'account_id': user.id,
        'nickname': user.nickname,
        'is_signup': True,
        'email': user.email
    })


@app.route('/connect/user/google', methods=['POST'])
@validate_args(GoogleAuthSchema())
def connect_user_with_google(args):
    authorization_code = args['authorization_code']

    flow = Flow.from_client_secrets_file(
        'credentials/google_client_secret.json',
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=config.GOOGLE_REDIRECT_URI,
    )

    flow.fetch_token(code=authorization_code)

    session = flow.authorized_session()
    user_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()
    print('user_info', user_info)
    google_id = user_info['id']
    google_name = user_info['name']
    email = user_info['email']

    if email not in config.WHITELIST_EMAILS:
        raise errors.PermissionDenied()

    user = UserModel.query.filter_by(google_id=google_id).first()

    if not user:
        user = UserModel(
            google_id=google_id,
            nickname=google_name,
            email=email,
        )
        user.save_to_db()

    return AccessTokenSchema().jsonify({
        'access_token': jwttoken.encode(user),
        'account_id': user.id,
        'nickname': user.nickname,
        'is_signup': False,
        'email': user.email,
    })
