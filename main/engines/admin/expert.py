from sqlalchemy import desc
from sqlalchemy.orm import contains_eager

from main import db
from main.enums import Topic
from main.models.expert import ExpertModel
from main.models.expert_topic import ExpertTopicModel
from main.models.expert_rank import ExpertRankModel


def search_experts(args):
    filters = []

    query = ExpertModel.query \
        .outerjoin(ExpertModel.expert_topics) \
        .options(contains_eager(ExpertModel.expert_topics))\
        .outerjoin(ExpertModel.expert_ranks) \
        .options(contains_eager(ExpertModel.expert_ranks))

    if args['ids']:
        filters.append(ExpertModel.id.in_(args['ids'].split(',')))
    if args['email']:
        filters.append(ExpertModel.email.like('%' + args['email'] + '%'))
    if args['topic_id'] != Topic.ALL:
        filters.append(ExpertTopicModel.topic_id == args['topic_id'])

    query = query.order_by(desc(ExpertModel.id))

    if filters:
        query = query.filter(*filters)

    print('query', query)
    paging = query.paginate(args['page'], args['items_per_page'], False)

    return paging


def delete_expert_topic(expert_id, topic_id):
    expert_topic = ExpertTopicModel.query\
        .filter_by(expert_id=expert_id, topic_id=topic_id).first()
    expert_rank = ExpertRankModel.query\
        .filter_by(expert_id=expert_id, topic_id=topic_id).first()

    if expert_topic:
        db.session.delete(expert_topic)
    if expert_rank:
        db.session.delete(expert_rank)
    db.session.commit()
