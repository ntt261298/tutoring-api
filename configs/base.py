class _BaseConfig(object):
    DEBUG = True

    JWT_SECRET = "random_secret_key"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost/thesis"

    WHITELIST_EMAILS = ["ntt261298@gmail.com", "truong@gotitapp.co"]
    GOOGLE_REDIRECT_URI = "http://localhost:3000"

    TEMPORARY_PASSWORD_LENGTH = 12
