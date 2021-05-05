from main.engines.tasks import pusher


def on_question_state_commit(question_state):
    if 'state' in question_state.get_tracked_changes():
        pusher.push_user_state.delay(question_state.user_id)


def on_expert_state_commit(expert_state):
    what_changed = expert_state.get_tracked_changes()
    if ('state' in what_changed) or ('connected' in what_changed):
        pusher.push_expert_state.delay(expert_state.expert_id)
