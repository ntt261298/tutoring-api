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


def create_subscription_package(db):
    from main.models.subscription_package import SubscriptionPackageModel
    db.session.add(
        SubscriptionPackageModel(
            name='Bundle Package',
            type='bundle',
            price=36,
            number_of_questions=3
        )
    )

    db.session.add(
        SubscriptionPackageModel(
            name='Monthly Subscription',
            type='monthly',
            price=150,
            number_of_questions=0
        )
    )

    db.session.add(
        SubscriptionPackageModel(
            name='Yearly Subscription',
            type='yearly',
            price=960,
            number_of_questions=0
        )
    )
    db.session.commit()
