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
    ROUTING_TIMEOUT = 60
    CHATTING_TIMEOUT = 120


class QuestionState:
    NOT_ROUTED = 'Not routed'
    NO_KING = 'No king'
    HAS_KING = 'Has king'
    WORKING = 'Working'
    COMPLETE = 'Complete'
    FAILED = 'Failed'
    RATING = 'Rating'


class PusherEvent:
    STATE_CHANGE = 'state_change'
