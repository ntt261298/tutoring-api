from google_auth_oauthlib.flow import Flow
from marshmallow import fields
from flask import jsonify

from config import config
from main import app
from main import db
from main.errors import PermissionDenied
from main.models.admin import AdminModel
from main.schemas.base import BaseSchema
from main.libs import jwttoken
from main.libs.validate_args import validate_args


class GoogleAuthSchema(BaseSchema):
    authorization_code = fields.String(required=True)


@app.route('/log-in/admin/google', methods=['POST'])
@validate_args(GoogleAuthSchema())
def log_in_admin_google(args):
    authorization_code = args['authorization_code']

    flow = Flow.from_client_secrets_file(
        'credentials/google_client_secret.json',
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=config.GOOGLE_REDIRECT_URI_ADMIN,
    )

    flow.fetch_token(code=authorization_code)

    session = flow.authorized_session()
    admin_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()
    print('admin_info', admin_info)
    google_id = admin_info['id']
    google_name = admin_info['name']
    email = admin_info['email']

    if email not in config.WHITELIST_EMAILS:
        raise PermissionDenied()

    admin = AdminModel.query.filter_by(google_id=google_id).first()

    if not admin:
        admin = AdminModel(
            google_id=google_id,
            google_name=google_name,
            email=email,
        )
        admin.save_to_db()

    return jsonify({
        'access_token': jwttoken.encode(admin),
        'account_id': admin.id,
        'account_name': admin.google_name,
    })
