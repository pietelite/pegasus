from .models import User


# Inserts the user into the database, returns the inserted User, or None if fail
def insert_user(email, username, password) -> User:
    # TODO implement
    user = User(email, username, password)
    return None


# Gets a User object from data from the database using either the username or email, returns None if no username exists
def get_user(login_id) -> User:
    # TODO implement
    if login_id == "pegasus":
        return User("pegasus@gmail.com", "pegasus", "pegasus")
    return None

