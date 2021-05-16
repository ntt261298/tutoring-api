from config import config
from main import pusher_client
from main.enums import PusherEvent
from main.libs.dict import merge_dicts
from main.models.question import QuestionModel


def parse_channel(channel_name):
    """
    Channel name format is:
    presence-<type>-<id>-<namespace>
    or presence-<type>-<namespace>

    1) type: user, expert, question
    2) id
    3) namespace: set from pusher.json, used for local development so that
    Local development is an isolated environment
    """
    channel = channel_name.split('-')
    optional_channel_info = {}
    if len(channel) == 4:
        namespace_index = 3
        try:
            optional_channel_info.update({'id': int(channel[2])})
        except ValueError:
            return None
    else:
        namespace_index = 2
    if channel[namespace_index] != config.PUSHER_CHANNEL_NAMESPACE:
        return None
    return merge_dicts({'type': channel[1]}, optional_channel_info)


def authenticate(request, account):
    # There are 3 valid pusher channels:
    #   1) presence-user-<id>-<namespace>: sends user status change
    #   2) presence-expert-<id>-<namespace>: sends expert status change
    #   3) presence-question-<id>-<namespace>: sends question status change
    channel = parse_channel(request.form['channel_name'])
    if not channel:
        return None
    auth = False

    if channel['type'] == account.account_type and channel['id'] == account.id:
        auth = True
    elif channel['type'] == 'question':
        query = QuestionModel.query. \
            filter_by(id=channel['id'])
        if account.account_type == 'user':
            query = query.filter(QuestionModel.user_id == account.id)
        else:
            query = query.filter(QuestionModel.expert_id == account.id)
        question = query.one_or_none()
        if question:
            auth = True
    if not auth:
        return None
    try:
        tmp = pusher_client.authenticate(
            channel=request.form['channel_name'],
            socket_id=request.form['socket_id'],
            custom_data={
                'user_id': '-'.join([account.account_type, str(account.id)]),
            })
    except:
        return None

    return tmp


def _get_account_channel_name(account_type, account_id):
    return '-'.join(['presence', account_type, str(account_id), config.PUSHER_CHANNEL_NAMESPACE])


def _get_question_channel_name(question_id):
    return '-'.join(['presence', 'question', str(question_id), config.PUSHER_CHANNEL_NAMESPACE])


def _get_presence_channel_name(name):
    return '-'.join(['presence', name, config.PUSHER_CHANNEL_NAMESPACE])


def _trigger_pusher(channel_name, event_type, data):
    pusher_client.trigger(channel_name, event_type, data)


def trigger_state_change(account_type, account_id, state):
    _trigger_pusher(_get_account_channel_name(account_type, account_id), PusherEvent.STATE_CHANGE, state)


def trigger_question_done(question_id):
    _trigger_pusher(_get_question_channel_name(question_id), PusherEvent.QUESTION_DONE, {})


def trigger_message(question_id, message):
    if message['message_type'] == 'file':
        _trigger_pusher(_get_question_channel_name(question_id), PusherEvent.NEW_MESSAGE, {"message_type": "file"})
    else:
        _trigger_pusher(_get_question_channel_name(question_id), PusherEvent.NEW_MESSAGE, message)
