from main import app, auth
from main.engines.state_machine import generate_expert_state
from main.schemas.state import ExpertStateSchema


@app.route('/expert/me/state', methods=['GET'])
@auth.requires_token_auth('expert')
def get_expert_state(expert):
    expert_state = generate_expert_state(expert.id)
    return ExpertStateSchema().jsonify(expert_state)
