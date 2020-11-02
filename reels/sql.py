from .models import User
from django.db import connection


def create_tables() -> None:
    with connection.cursor() as cursor:
        # Create Users
        cursor.execute("""
        CREATE TABLE Users (
            UserId CHAR(32) NOT NULL PRIMARY KEY,
            UserName VARCHAR(255) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL,
            Email VARCHAR(255) NOT NULL UNIQUE,
            Created BIGINT NOT NULL,
            LastSeen BIGINT NOT NULL,
            Verified BIT DEFAULT 0
        );
        """)

        # Create Videos
        cursor.execute("""
        CREATE TABLE Videos (
            VideoId CHAR(32) NOT NULL PRIMARY KEY,
            UserId CHAR(32) NOT NULL FOREIGN KEY REFERENCES Users(UserId),
            Created BIGINT NOT NULL,
        );
        """)

        # Create Posts
        cursor.execute("""
        CREATE TABLE Posts (
            PostId CHAR(32) NOT NULL PRIMARY KEY,
            VideoId CHAR(32) NOT NULL FOREIGN KEY REFERENCES Videos(VideoId) ON DELETE CASCADE,
            Description TEXT,
            Created BIGINT NOT NULL,
            Likes INT NOT NULL DEFAULT 0
        );
        """)

        # Create Likes
        cursor.execute("""
        CREATE TABLE Likes (
            UserId CHAR(32) NOT NULL FOREIGN KEY REFERENCES Users(UserId) ON DELETE CASCADE,
            PostId CHAR(32) NOT NULL FOREIGN KEY REFERENCES Posts(PostId) ON DELETE CASCADE
        );
        """)

        # Create Tags
        cursor.execute("""
        CREATE TABLE Tags (
            Name VARCHAR(225) NOT NULL,
            PostId CHAR(32) NOT NULL FOREIGN KEY REFERENCES Posts(PostId) ON DELETE CASCADE
        );
        """)


# Inserts the user into the database, returns the inserted User, or None if fail
def insert_user(email, username, password) -> User:
    user = User(email, username, password)
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO Users VALUES ('{}', '{}', '{}', '{}', '{}', '{}', 0)"
                       .format(str(user.user_id).replace('-', ''), user.user_name, user.password,
                               user.email, int(user.created), int(user.last_online)))
    return None


# Gets a User object from data from the database using either the username or email, returns None if no username exists
def get_user(credential) -> User:
    # TODO implement
    with connection.cursor() as cursor:
        query = "SELECT * FROM Users WHERE UserName = '{}' OR Email = '{}'".format(credential, credential)
        cursor.execute(query)
        row = cursor.fetchone()
    if row:
        return User(row[1], row[2], row[3], row[4], row[5], row[6])
    return None


# Inserts a video


# Toggles a like on a video, returns new like status
def toggle_like(user_id, video_id) -> bool:
    # TODO implement
    return True


# Returns whether a video has a video has a like on it
def has_liked(user_id, video_id) -> bool:
    # TODO implement
    return False


# Return number of likes on a video
def likes_count(video_id) -> int:
    # TODO implement
    return 0
