from re import fullmatch
from .sql import get_user_by_credential
from .config import USERNAME_LENGTH_MIN, USERNAME_LENGTH_MAX, USERNAME_REGEX, \
    PASSWORD_LENGTH_MIN, PASSWORD_LENGTH_MAX, PASSWORD_REGEX, \
    EMAIL_REGEX

# "Valid" means the input is in the correct format
# "Correct" means some combination matches our records
# "Exists" means some single data matches our records


# check if email is valid, returns list of all errors
def valid_email(email) -> list:
    errors = []
    if not fullmatch(EMAIL_REGEX, email):
        errors.append('This isn\'t an email')
    return errors


# check if username is valid, returns list of all errors
def valid_username(username) -> list:
    errors = []
    if len(username) < USERNAME_LENGTH_MIN:
        errors.append('Your username must be at least {} characters'.format(USERNAME_LENGTH_MIN))
    if len(username) > USERNAME_LENGTH_MAX:
        errors.append('Your username cannot be larger than {} characters'.format(USERNAME_LENGTH_MAX))
    if not fullmatch(USERNAME_REGEX, username):
        # Username doesn't match regex string
        errors.append('Your username must only contain numbers, letters, periods, dashes, or underscores')
    return errors


# check if password is valid, returns list of all errors
def valid_password(password) -> list:
    errors = []
    if len(password) < PASSWORD_LENGTH_MIN:
        errors.append('Your password must be at least {} characters'.format(PASSWORD_LENGTH_MIN))
    if len(password) > PASSWORD_LENGTH_MAX:
        errors.append('Your password cannot be larger than {} characters'.format(PASSWORD_LENGTH_MAX))
    if not fullmatch(PASSWORD_REGEX, password):
        # Username doesn't match regex string
        errors.append('Your username must only contain numbers, letters, and these: !@#$%^&*()[]{},./<>?')
    return errors


# check if credentials are correct, returns list of all errors
def correct_credentials(login_id, password) -> list:
    errors = existing_user(login_id)
    user = get_user_by_credential(login_id)
    if user and not password == get_user_by_credential(login_id).password:
        errors.append('That\'s not the right password')
    return errors


# check if a username or email exists
def existing_user(login_id) -> list:
    errors = []
    if not get_user_by_credential(login_id):
        errors.append('It appears that you, {}, don\'t exist yet'.format(login_id))
    return errors
