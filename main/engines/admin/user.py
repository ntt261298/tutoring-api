from sqlalchemy import desc

from main.models.user import UserModel


def search_users(args):
    filters = []

    query = UserModel.query

    if args['ids']:
        filters.append(UserModel.id.in_(args['ids'].split(',')))
    if args['email']:
        filters.append(UserModel.email.like('%' + args['email'] + '%'))

    query = query.order_by(desc(UserModel.id))

    if filters:
        query = query.filter(*filters)

    print('query', query)
    paging = query.paginate(args['page'], args['items_per_page'], False)

    return paging
