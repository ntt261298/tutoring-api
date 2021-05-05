def create(db):
    for function_name, function in list(globals().items()):
        if callable(function) and function_name.startswith('create_'):
            function(db)


def create_topics(db):
    from main.models.topic import TopicModel
    db.session.add(
        TopicModel(
            name='Math',
        )
    )

    db.session.add(
        TopicModel(
            name='English',
        )
    )
    db.session.commit()
