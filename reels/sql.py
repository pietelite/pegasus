from .models import User


# Inserts the user into the database, returns the inserted User, or None if fail
def insert_user(username, password, email) -> User:
    # TODO implement
    user = User(username, password)
    return None


# Gets a User object from data from the database
def get_user(username) -> User:
    # TODO implement
    return None


# Queries database to get whether a user exists. True if exists in database, False if not.
def username_exists(username) -> bool:
    # TODO implement
    return True


# Queries database to get a user's password. Returns None if cannot find user.
def get_password(username) -> str:
    # TODO implement
    return "test"
