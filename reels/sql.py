from .models import User, Video, Like, PostTag, Post
from django.db import connection

from .util import str_to_uuid, uuid_to_str


def init_database() -> None:
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
            Title VARCHAR(255) NOT NULL,
            Description TEXT,
            Created BIGINT NOT NULL,
            Likes INT NOT NULL DEFAULT 0,
        );
        """)

        # Create Likes
        cursor.execute("""
        CREATE TABLE Likes (
            UserId CHAR(32) NOT NULL FOREIGN KEY REFERENCES Users(UserId) ON DELETE CASCADE,
            PostId CHAR(32) NOT NULL FOREIGN KEY REFERENCES Posts(PostId) ON DELETE CASCADE,
            Timestamp BIGINT NOT NULL
        );
        """)

        # Create Tags
        cursor.execute("""
        CREATE TABLE Tags (
            Name VARCHAR(225) NOT NULL,
            PostId CHAR(32) NOT NULL FOREIGN KEY REFERENCES Posts(PostId) ON DELETE CASCADE
        );
        """)

        # Create stored procedure for updating likes
        cursor.execute("""
        CREATE PROCEDURE UpdateSinglePostLikesCount @post_id char(32)
        AS 
        UPDATE Posts 
        SET Posts.Likes = (SELECT COUNT(Likes.UserId) FROM Likes WHERE Likes.PostId = @post_id GROUP BY PostId) 
        WHERE Posts.PostId = @post_id
        """)

        # Create Trigger for Updating and Inserting values from the Likes table
        cursor.execute("""
        CREATE TRIGGER UpdateSinglePostLikesCountTrigger
            ON Likes 
            AFTER UPDATE, INSERT
        AS
            DECLARE @post_id CHAR(32)
            SELECT @post_id = inserted.PostId FROM inserted
            EXEC [dbo].[UpdateSinglePostLikesCount] @post_id;
        """)

        # Create Trigger for Deleting values from the Likes table
        cursor.execute("""
        CREATE TRIGGER UpdateSinglePostLikesCountTriggerDelete
            ON Likes 
            AFTER DELETE
        AS
            DECLARE @post_id CHAR(32)
            SELECT @post_id = deleted.PostId FROM deleted
            EXEC [dbo].[UpdateSinglePostLikesCount] @post_id;
        """)


# === USERS ===

# Inserts the user into the database
def insert_user(user: User) -> None:
    with connection.cursor() as cursor:
        query = ("INSERT INTO Users VALUES ('{}', '{}', '{}', '{}', '{}', '{}', 0)"
                 .format(uuid_to_str(user.user_id), user.user_name, user.password,
                         user.email, int(user.created), int(user.last_online)))
        cursor.execute(query)


# Delete user information from database
def delete_user(user_id: str) -> None:
    with connection.cursor() as cursor:
        query = "DELETE FROM Users WHERE UserId = '{}'".format(user_id)
        cursor.execute(query)


# Gets a User object from data from the database using either the username or email, returns None if no username exists
def get_user(username_or_email: str) -> User:
    with connection.cursor() as cursor:
        query = "SELECT * FROM Users WHERE UserName = '{}' OR Email = '{}'".format(username_or_email, username_or_email)
        cursor.execute(query)
        row = cursor.fetchone()
    if row:
        return User(row[1], row[2], row[3], str_to_uuid(row[0]), row[4], row[5], row[6])
    raise ValueError('This user id is not valid')


# === VIDEOS AND TAGS ===

# Inserts video information to relational database. This does not do anything with the actual video.
def insert_video(video: Video) -> None:
    with connection.cursor() as cursor:
        query = "INSERT INTO Videos VALUES ('{}', '{}', '{}')" \
            .format(uuid_to_str(video.video_id), video.user_id, video.created)
        cursor.execute(query)


# Deletes video information from relational database. This does not do anything with the actual video.
def delete_video(video_id: str) -> None:
    with connection.cursor() as cursor:
        query = "DELETE FROM Videos WHERE VideoId = '{}'".format(video_id)
        cursor.execute(query)


# Gets video information if it exists. If it doesn't exist, return None
def get_video(video_id: str) -> Video:
    with connection.cursor() as cursor:
        query = "SELECT * FROM Videos WHERE VideoId = '{}'".format(video_id)
        cursor.execute(query)
        row = cursor.fetchone()
    if row:
        return Video(row[1], str_to_uuid(row[0]), row[2])
    raise ValueError('This video id is not valid')


# === POSTS, TAGS, AND LIKES ===

# Inserts a post to database, assuming the corresponding video information has already been inserted
def insert_post(post: Post) -> None:
    with connection.cursor() as cursor:
        query = "INSERT INTO Posts VALUES ('{}', '{}', '{}', '{}', 0)" \
            .format(post.post_id, post.video_id, post.description, post.created)
        cursor.execute(query)


# Deletes a post from database
def delete_post(post_id: str) -> None:
    with connection.cursor() as cursor:
        query = "DELETE FROM Posts WHERE PostId = '{}'".format(post_id)
        cursor.execute(query)


# Gets a post from database
def get_post(post_id: str) -> Post:
    with connection.cursor() as cursor:
        query = "SELECT * FROM Posts WHERE PostId = '{}'".format(post_id)
        cursor.execute(query)
        row = cursor.fetchone()
    if row:
        return Post(row[1], row[2], row[3], str_to_uuid(row[0]), row[4], row[5])
    raise ValueError('This video id is not valid')


# Adds a tag to a video
def add_tag(post_tag: PostTag) -> None:
    with connection.cursor() as cursor:
        query = "INSERT INTO Tags VALUES ('{}', '{}')".format(post_tag.tag_name.lower(), post_tag.post_id)
        cursor.execute(query)


# Removes a tag from a video
def remove_tag(post_tag: PostTag) -> None:
    with connection.cursor() as cursor:
        query = "DELETE FROM Tags WHERE Name = '{}' AND PostId = '{}'" \
            .format(post_tag.tag_name.lower(), post_tag.post_id)
        cursor.execute(query)


# Returns whether a video has a video has a like on it
def has_liked(user_id: str, video_id: str) -> bool:
    with connection.cursor() as cursor:
        query = "SELECT * FROM Likes WHERE UserId = '{}' AND VideoId = '{}'".format(user_id, video_id)
        cursor.execute(query)
        row = cursor.fetchone()
    return bool(row)


# Toggles a like on a video, returns new like status
def toggle_like(user_id: str, video_id: str) -> bool:
    if has_liked(user_id, video_id):
        query = "DELETE FROM Likes WHERE UserId = '{}' AND VideoId = '{}'".format(user_id, video_id)
        now_liked = False
    else:
        like = Like(user_id, video_id)
        query = "INSERT INTO Likes VALUES ('{}', '{}', '{}')".format(like.user_id, like.video_id, like.timestamp)
        now_liked = True
    with connection.cursor() as cursor:
        cursor.execute(query)
    return now_liked


# Return number of likes on a video
def likes_count(post_id: str) -> int:
    with connection.cursor() as cursor:
        query = "SELECT Likes FROM Posts WHERE PostId = '{}'".format(post_id)
        cursor.execute(query)
        row = cursor.fetchone()
    return int(row[0])
