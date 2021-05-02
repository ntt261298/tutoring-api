from main import app, auth, db
from main.schemas.base import BaseSchema
from main.models.expert_state import ExpertStateModel
from main.enums import ExpertState


@app.route('/expert/me/connections', methods=['POST'])
@auth.requires_token_auth('expert')
def create_expert_connection(expert):
    # First time posting question
    if expert.expert_state is None:
        expert_state = ExpertStateModel(
            expert_id=expert.id,
            state=ExpertState.NOT_ROUTED,
        )
        expert.expert_state = expert_state

    expert.expert_state.connected = True
    db.session.commit()

    return BaseSchema().jsonify({})


@app.route('/expert/me/connections', methods=['DELETE'])
@auth.requires_token_auth('expert')
def delete_expert_connection(expert):
    if expert.expert_state:
        expert.expert_state.connected = False
        db.session.commit()

    return BaseSchema().jsonify({})
