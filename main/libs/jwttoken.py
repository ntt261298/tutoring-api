import os
import datetime

import jwt

from config import config


def encode(account):
    iat = datetime.datetime.utcnow()
    return jwt.encode({
        'sub': account.id,
        'iat': iat,
        'exp': iat + datetime.timedelta(days=365),
        'nonce': account.access_token_nonce,
    }, config.JWT_SECRET)


def decode(access_token, audience):
    try:
        token = jwt.decode(access_token, config.JWT_SECRET, leeway=10, algorithms="HS256", audience=audience)
    except jwt.InvalidTokenError:
        return None
    return token


def generate_access_token_nonce():
    return os.urandom(4).hex()
