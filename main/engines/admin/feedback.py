from sqlalchemy import desc

from main import db
from main.models.feedback import FeedbackModel
from main.models.expert import ExpertModel
from main.models.user import UserModel
from main.enums import AccountType


def search_feedback(args):
    filters = []
    query = db.session.query

    if args['account_type'] == AccountType.USER:
        query = query(UserModel, FeedbackModel)\
                      .filter(UserModel.id == FeedbackModel.user_id)
        filters.append(UserModel.email.like('%' + args['email'] + '%'))
    if args['account_type'] == AccountType.EXPERT:
        query = query(ExpertModel, FeedbackModel)\
                     .filter(ExpertModel.id == FeedbackModel.expert_id)
        filters.append(ExpertModel.email.like('%' + args['email'] + '%'))

    if args['content']:
        filters.append(FeedbackModel.content.like('%' + args['content'] + '%'))

    query = query.order_by(desc(FeedbackModel.id))

    if filters:
        query = query.filter(*filters)

    print('query', query)
    paging = query.paginate(args['page'], args['items_per_page'], False)

    return paging
