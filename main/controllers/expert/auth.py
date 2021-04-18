from marshmallow import fields, validate
from google_auth_oauthlib.flow import Flow

from config import config
from main import app
from main.models.expert import ExpertModel
from main.schemas.base import BaseSchema
from main.schemas.user import AccessTokenSchema
from main.libs.validate_args import validate_args
from main.libs import pw, jwttoken
from main import errors


class ExpertLoginSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class GoogleAuthSchema(BaseSchema):
    authorization_code = fields.String(required=True)


@app.route('/log-in/expert/email', methods=['POST'])
@validate_args(ExpertLoginSchema())
def log_in_expert_email(args):
    expert = ExpertModel.query. \
        filter_by(email=args['email']). \
        one_or_none()
    if not expert:
        raise errors.AccountNotExisted()
        # Check if the password is correct
    if not expert.password_hash or not expert.password_salt:
        raise errors.EmailAndPasswordNotMatch()
    try:
        if expert.password_hash != pw.generate_hash(args['password'], expert.password_salt):
            raise errors.EmailAndPasswordNotMatch()
    except ValueError:
        raise errors.EmailAndPasswordNotMatch()

    return AccessTokenSchema().jsonify({
        'access_token': jwttoken.encode(expert),
        'account_id': expert.id,
        'name': expert.nickname,
        'is_signup': False,
        'email': expert.email,
    })


@app.route('/connect/expert/google', methods=['POST'])
@validate_args(GoogleAuthSchema())
def connect_expert_with_google(args):
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
    expert_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()
    print('expert_info', expert_info)
    google_id = expert_info['id']
    google_name = expert_info['name']
    email = expert_info['email']

    if email not in config.WHITELIST_EMAILS:
        raise errors.PermissionDenied()

    expert = ExpertModel.query.filter_by(google_id=google_id).first()

    if not expert:
        expert = ExpertModel(
            google_id=google_id,
            nickname=google_name,
            email=email,
        )
        expert.save_to_db()

    return AccessTokenSchema().jsonify({
        'access_token': jwttoken.encode(expert),
        'account_id': expert.id,
        'nickname': expert.nickname,
        'is_signup': False,
        'email': expert.email,
    })
