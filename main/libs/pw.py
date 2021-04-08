import os
import random

from Crypto.Hash import SHA256

from config import config


def generate_salt():
    return os.urandom(8).hex()


# Raise ValueError exception when password or salt not a valid ASCII string
def generate_hash(password, salt):
    h = SHA256.new()
    try:
        h.update(salt.encode('ascii'))
        h.update(password.encode('ascii'))
    except UnicodeEncodeError:
        raise ValueError
    digest = h.hexdigest()
    return digest


def generate_password(password):
    # Generate password hash and salt
    password_salt = generate_salt()
    password_hash = generate_hash(password, password_salt)
    return password_salt, password_hash


def generate_temporary_password():
    """
    Randomly generate a password with a fixed length, no duplicate characters in the password
    :return: generated password
    """
    s = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&'()*+,-./:;<=>?@[]^_`|~"
    return "".join(random.sample(s, config.TEMPORARY_PASSWORD_LENGTH))
