class AccountType:
    ADMIN = 'admin'
    USER = 'user'
    EXPERT = 'expert'


class SubscriptionType:
    BUNDLE = 'bundle'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'


class SubscriptionStatus:
    ACTIVE = 'active'
    TERMINATED = 'terminated'


class Topic:
    MATH = 1
    ENGLISH = 2
    ALL = 3


class AccountStatus:
    ACTIVE = 'active'
    DELETED = 'deleted'


class ExpertState:
    NOT_ROUTED = 'Not routed'
    BIDDING = 'Bidding'
    KING = 'King'
    WORKING = 'Working'
    RATING = 'Rating'


class RREConfig:
    ROUTING_TIMEOUT = 40
    CHATTING_TIMEOUT = 120


class PusherEvent:
    STATE_CHANGE = 'state_change'
    QUESTION_DONE = 'question_done'
    NEW_MESSAGE = 'new_message'


class ReferenceFileType:
    QUESTION_DESCRIPTION = 'question description'


class RouteState:
    BIDDING = 'Bidding'
    KING = 'King'
    WORKING = 'Working'
    TIMEOUT = 'Timeout'
    SKIPPED = 'Skipped'
    COMPLETE = 'Complete'
    RATING = 'Rating'
    LOST = 'Lost'


class SentinelRouteState:
    ROUTED = 'Routed'
    SUCCESS = 'Success'
    FAILED = 'Failed'


class QuestionState:
    NOT_ROUTED = 'Not routed'
    NO_KING = 'No king'
    HAS_KING = 'Has king'
    WORKING = 'Working'
    COMPLETE = 'Complete'
    FAILED = 'Failed'
    RATING = 'Rating'

    @staticmethod
    def get_finished_states():
        return [QuestionState.COMPLETE, QuestionState.FAILED]

    @staticmethod
    def get_rating_required_states():
        return [QuestionState.RATING]

    @classmethod
    def get_pre_session_states(cls):
        return [cls.NOT_ROUTED, cls.NO_KING, cls.HAS_KING]

    @classmethod
    def get_in_session_states(cls):
        return [cls.WORKING]

    @classmethod
    def get_post_session_states(cls):
        return [cls.COMPLETE, cls.RATING, cls.FAILED]


class EndSessionReason:
    USER_END = 'user end'
    CHATTING_TIMEOUT = 'chatting timeout'


class RatingScore:
    MAXIMUM_SCORE = 5
    MINIMUM_SCORE = 1
