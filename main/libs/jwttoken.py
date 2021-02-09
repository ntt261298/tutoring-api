import os


def generate_access_token_nonce():
    return os.urandom(4).hex()
