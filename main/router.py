from main.enums import QuestionState
from main.engines.tasks.router import handle_route_timeout, handle_question_created


# The commit hook for when question_state changes
def on_question_state_commit(question_state):
    question_id = question_state.question_id
    state = question_state.state
    what_changed = question_state.get_tracked_changes()
    if ('state' not in what_changed) and \
            ('num_bidding' not in what_changed):
        return
    if state == QuestionState.NOT_ROUTED:
        handle_question_created.s(question_id).apply_async(countdown=3)
    elif (state in (QuestionState.NO_KING, QuestionState.HAS_KING)) and \
            (question_state.num_bidding == 0):
        handle_route_timeout.delay(question_id)
