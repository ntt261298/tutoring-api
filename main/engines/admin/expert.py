from sqlalchemy import desc

from main.models.expert import ExpertModel
from main.models.expert_topic import ExpertTopicModel


def search_experts(args):
    filters = []

    query = ExpertModel.query

    if args['ids']:
        filters.append(ExpertModel.id.in_(args['ids'].split(',')))
    if args['email']:
        filters.append(ExpertModel.email.like('%' + args['email'] + '%'))
    if args['topic_id']:
        query = query.outerjoin(ExpertModel.expert_topics)
        filters.append(ExpertTopicModel.topic_id == args['topic_id'])

    query = query.outerjoin(ExpertModel.expert_ranks)
    query = query.order_by(desc(ExpertModel.id))

    if filters:
        query = query.filter(*filters)

    paging = query.paginate(args['page'], args['items_per_page'], False)

    return paging
