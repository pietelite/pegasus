from typing import Union, List

from ..models import User, Video, Like, PostTag, Post
from django.db import connection

from ..sql.sql import SqlHandlerInterface


class SqlServerHandler(SqlHandlerInterface):
    # Initialize all objects in database
    def init_database(self) -> None:
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
                Preset VARCHAR(255) NOT NULL,
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
            SET Posts.Likes = ISNULL((SELECT COUNT(Likes.UserId) FROM Likes WHERE Likes.PostId = @post_id GROUP BY PostId), 0)
            WHERE Posts.PostId = @post_id
            """)

            # Create Trigger for Updating and Inserting values from the Likes table
            cursor.execute("""
            CREATE TRIGGER UpdateSinglePostLikesCountTriggerInsert
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
    def insert_user(self, user: User) -> None:
        with connection.cursor() as cursor:
            query = "INSERT INTO Users VALUES (" \
                    f"'{user.user_id}', " \
                    f"'{user.user_name}', " \
                    f"'{user.password}', " \
                    f"'{user.email}', " \
                    f"'{int(user.created)}', " \
                    f"'{int(user.last_online)}', " \
                    "0)"
            cursor.execute(query)

    # Delete user information from database
    def delete_user(self, user_id: str) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM Users WHERE UserId = '{user_id}'"
            cursor.execute(query)

    # Get a User object from data from the database using the user_id
    def get_user(self, user_id: str) -> Union[User, None]:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Users WHERE UserId = '{user_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return User(row[1], row[2], row[3], row[0], row[4], row[5], row[6])
        return None

    # Gets a User object from data from the database using either the username or email
    def get_user_by_credential(self, username_or_email: str) -> Union[User, None]:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Users WHERE UserName = '{username_or_email}' OR Email = '{username_or_email}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return User(row[1], row[2], row[3], row[0], row[4], row[5], row[6])
        return None

    # === VIDEOS AND TAGS ===

    # Inserts video information to relational database. This does not do anything with the actual video.
    def insert_video(self, video: Video) -> None:
        with connection.cursor() as cursor:
            query = f"INSERT INTO Videos VALUES ('{video.video_id}', '{video.user_id}', '{video.preset}', '{video.created}')"
            cursor.execute(query)

    # Deletes video information from relational database. This does not do anything with the actual video.
    def delete_video(self, video_id: str) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM Videos WHERE VideoId = '{video_id}'"
            cursor.execute(query)

    # Gets video information if it exists. If it doesn't exist, return None
    def get_video(self, video_id: str) -> Union[Video, None]:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Videos WHERE VideoId = '{video_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return Video(row[1], row[0], row[2], row[3])
        return None

    def get_videos_by_user_id(self, user_id: str) -> List[Video]:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Videos WHERE UserId = '{user_id}'"
            cursor.execute(query)
            rows = cursor.fetchall()
        return [Video(row[1], row[0], row[2], row[3]) for row in rows]

    # === POSTS, TAGS, AND LIKES ===

    # Inserts a post to database, assuming the corresponding video information has already been inserted
    def insert_post(self, post: Post) -> None:
        with connection.cursor() as cursor:
            query = "INSERT INTO Posts VALUES (" \
                    f"'{post.post_id}', " \
                    f"'{post.video_id}', " \
                    f"'{self.escape_apostrophes(post.title)}', " \
                    f"'{self.escape_apostrophes(post.description)}', " \
                    f"'{post.created}', " \
                    f"0) "
            cursor.execute(query)

    # Deletes a post from database
    def delete_post(self, post_id: str) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM Posts WHERE PostId = '{post_id}'"
            cursor.execute(query)

    # Updates a post
    def update_post(self, post_id: str, title: str, description: str) -> None:
        with connection.cursor() as cursor:
            query = "UPDATE Posts SET " \
                    f"Title='{self.escape_apostrophes(title)}', Description='{self.escape_apostrophes(description)}' " \
                    f"WHERE PostId='{post_id}'"
            cursor.execute(query)

    # Gets a post from database
    def get_post(self, post_id: str) -> Union[Post, None]:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Posts WHERE PostId = '{post_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return Post(row[1], row[2], row[3], row[0], row[4], row[5])
        return None

    # Get all posts owned by a user
    def get_post_ids_by_user_id(self, user_id: str) -> list:
        with connection.cursor() as cursor:
            query = f"SELECT Posts.PostId FROM Posts INNER JOIN Videos ON Posts.VideoId = Videos.VideoId WHERE Videos.UserId = '{user_id}'"
            cursor.execute(query)
            rows = cursor.fetchall()
        return [row[0] for row in rows]

    # Gets all PostId's, ordered most recent first
    def get_all_post_ids(self) -> list:
        # TODO trim this function to only include a subset of all posts somehow
        with connection.cursor() as cursor:
            query = "SELECT PostId FROM Posts ORDER BY Created DESC"
            cursor.execute(query)
            postsdb = cursor.fetchall()

        if postsdb:
            postids = []
            for pdb in postsdb:
                postids.append(pdb[0])

            return postids

        return []

    # Adds a tag to a video. Forces tag to be lowercase
    def add_tag(self, post_tag: PostTag) -> None:
        with connection.cursor() as cursor:
            query = f"INSERT INTO Tags VALUES ('{post_tag.tag_name.lower()}', '{post_tag.post_id}')"
            cursor.execute(query)

    # Removes a tag from a video.
    def remove_tag(self, post_tag: PostTag) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM Tags WHERE Name = '{post_tag.tag_name.lower()}' AND PostId = '{post_tag.post_id}'"
            cursor.execute(query)

    # Returns whether a video has a video has a like on it
    def has_liked(self, user_id: str, post_id: str) -> bool:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Likes WHERE UserId = '{user_id}' AND PostId = '{post_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        return bool(row)

    # Toggles a like on a video, returns new like status
    def toggle_like(self, user_id: str, post_id: str) -> bool:
        print(user_id)
        print(post_id)
        if self.has_liked(user_id, post_id):
            query = f"DELETE FROM Likes WHERE UserId = '{user_id}' AND PostId = '{post_id}'"
            now_liked = False
        else:
            like = Like(user_id, post_id)
            query = f"INSERT INTO Likes VALUES ('{like.user_id}', '{like.post_id}', '{like.timestamp}')"
            now_liked = True
        with connection.cursor() as cursor:
            cursor.execute(query)
        return now_liked

    # Return number of likes on a video
    def likes_count(self, post_id: str) -> int:
        with connection.cursor() as cursor:
            query = f"SELECT Likes FROM Posts WHERE PostId = '{post_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        return int(row[0])

    # Get admin user, which is also the user which owns all
    def get_admin_user(self) -> User:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM Users WHERE UserId = '{'0' * 32}'"
            cursor.execute(query)
            row = cursor.fetchone()
        return User(row[1], row[2], row[3], row[0], row[4], row[5], row[6])

    def escape_apostrophes(self, s: str) -> str:
        return s.replace('\'', '\'\'')

    # AGGREGATES AND SEQUENCES

    def get_users_post_count(self) -> list:
        with connection.cursor() as cursor:
            query = """
    SELECT Videos.UserID, COUNT(PostID) as NumPosts
    FROM Videos JOIN Posts ON Posts.VideoID = Videos.VideoID
    GROUP BY Videos.UserId
    ORDER BY NumPosts DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
        return rows

    def tear_down_database(self) -> None:
        if input("""
    Are you sure you want to reset the entire database?
    This will delete all data and you will have to run init_database to reinitialize.
    Type "yes" to continue, or something else to exit.
        """).lower() == 'yes':
            with connection.cursor() as cursor:
                cursor.execute("""
    DROP TRIGGER UpdateSinglePostLikesCountTriggerDelete;
    DROP TRIGGER UpdateSinglePostLikesCountTrigger;
    DROP PROCEDURE UpdateSinglePostLikesCount;
    DROP TABLE Tags;
    DROP TABLE Likes;
    DROP TABLE Posts;
    DROP TABLE Videos;
    DROP TABLE Users;
            """)
                print('Database torn down')
