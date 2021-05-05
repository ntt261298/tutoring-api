from main import app, auth
from main.engines.state_machine import generate_user_state
from main.schemas.state import UserStateSchema


@app.route('/user/me/state', methods=['GET'])
@auth.requires_token_auth('user')
def get_user_state(user):
    user_state = generate_user_state(user.id)

    return UserStateSchema().jsonify(user_state)
