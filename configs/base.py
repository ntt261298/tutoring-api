class _BaseConfig(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost/thesis"

    WHITELIST_DOMAINS = ['gmail.com']
    GOOGLE_REDIRECT_URI = 'http://localhost:3000'
