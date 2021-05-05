from flask import request, jsonify

from main import app, errors, auth
from main.engines import pusher


@app.route('/expert/me/pusher/auth', methods=['POST'])
@auth.requires_token_auth('expert')
def get_pusher_token_for_expert(expert):
    response = pusher.authenticate(request, expert)
    if not response:
        raise errors.Unauthorized()
    return jsonify(response)


@app.route('/user/me/pusher/auth', methods=['POST'])
@auth.requires_token_auth('user')
def get_pusher_token_for_user(user):
    response = pusher.authenticate(request, user)
    if not response:
        raise errors.Unauthorized()
    return jsonify(response)
