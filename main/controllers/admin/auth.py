from google_auth_oauthlib.flow import Flow
from marshmallow import Schema, fields
from flask import jsonify

from config import config
from main import app
from main import db
from main.errors import PermissionDenied
from main.models.admin import AdminModel
from main.libs import jwttoken
from main.libs.validate_args import validate_args


class GoogleAuthSchema(Schema):
    id_token = fields.String(required=True)


@app.route('/log-in/admin/google', method=['POST'])
@validate_args(GoogleAuthSchema())
def log_in_admin_google(args):
    authorization_code = args['authorization_code']

    flow = Flow.from_client_secrets_file(
        'credentials/google_client_secret.json',
        scopes=['profile', 'email'],
        redirect_uri=config.GOOGLE_REDIRECT_URI
    )

    flow.fetch_token(code=authorization_code)

    session = flow.authorized_session()
    user_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()
    google_id = user_info['sub']
    hosted_domain = user_info['hd']
    name = user_info['name'] or {}

    if hosted_domain not in config.WHITELIST_DOMAINS:
        raise PermissionDenied()

    user = AdminModel.query.filter_by(google_id=google_id).first()

    if not user:
        user = AdminModel(
            google_id=google_id,
            email=user_info['email'],
            google_first_name=name.get('givenName') or '',
            google_last_name=name.get('familyName') or ''
        )
        db.session.add(user)
    db.session.commit()

    user_name = user.google_first_name + ' ' + user.google_last_name

    return jsonify({
        'access_token': jwttoken.encode(user),
        'account_id': user.id,
        'account_name': user_name,
        'account_type': 'admin',
        'auth_type': 'google'
    })
