from re import fullmatch
from .sql import username_exists, get_password
from .config import USERNAME_LENGTH_MIN, USERNAME_LENGTH_MAX, USERNAME_REGEX


# check if username is valid, returns list of all errors
def valid_username_string(username) -> list:
    errors = []
    if len(username) < USERNAME_LENGTH_MIN:
        errors.append('Your username must be at least {} characters'.format(USERNAME_LENGTH_MIN))
    if len(username) > USERNAME_LENGTH_MAX:
        errors.append('Your username cannot be larger than {} characters'.format(USERNAME_LENGTH_MAX))
    if not fullmatch(USERNAME_REGEX, username):
        # Username doesn't match regex string
        print(username)
        print(fullmatch(USERNAME_REGEX, username))
        print(USERNAME_REGEX)
        errors.append('Your username must only contain numbers, letters, periods, dashes, or underscores')
    return errors


# check if valid credentials, returns list of all errors
def valid_credentials(username, password) -> list:
    errors = []
    if not username_exists(username):
        errors.append('That username doesn\'t exist!')
    elif not password == get_password(username):
        errors.append('That\'s not the right password')
    return errors
