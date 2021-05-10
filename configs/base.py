class _BaseConfig(object):
    DEBUG = True

    JWT_SECRET = "random_secret_key"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost/thesis"

    WHITELIST_EMAILS = ["ntt261298@gmail.com", "truong@gotitapp.co"]
    GOOGLE_REDIRECT_URI_ADMIN = "http://localhost:3000"
    GOOGLE_REDIRECT_URI_USER = "http://localhost:9000"


    TEMPORARY_PASSWORD_LENGTH = 12

    BRAINTREE_ENVIRONMENT = 'sandbox'
    BRAINTREE_MERCHANT_ID = 'rq4z9ckgv599kpz3'
    BRAINTREE_PRIVATE_KEY = 'dd4adafb49d2d0d61e7d7dbf206a82b0'
    BRAINTREE_PUBLIC_KEY = 'z379x5hhv2z7c596'
    BRAINTREE_EMAIL_SUPPORT = 'ntt261298@gmail.com'

    FIXED_BID_AMOUNT = 8

    PUSHER_CHANNEL_NAMESPACE = 'tutoring'
    PUSHER_APP_ID = '1197322'
    PUSHER_KEY = '5bbce7630a816f302c2f'
    PUSHER_SECRET = '63874fa2780dd2b7b872'
    PUSHER_CLUSTER = 'ap1'

    REQUEST_DEADLINE = 60

    CELERY_BROKER_URL = 'redis://localhost:6379',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
