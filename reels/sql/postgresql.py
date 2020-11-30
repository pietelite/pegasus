from abc import ABC
from os import environ
from typing import Union, List, Optional

from overrides import overrides

from ..models import User, Video, Like, PostTag, Post, SessionClip, SessionAudio
from django.db import connection

from .sql import SqlHandlerInterface


class PostgreSqlHandler(SqlHandlerInterface, ABC):
    # TODO make all inserts specify which columns its inserting all values
    # Initialize all objects in database
    @overrides
    def init_database(self) -> None:
        with connection.cursor() as cursor:
            # Create Tables
            cursor.execute(f"""
/* users */
CREATE TABLE IF NOT EXISTS users (
    user_id CHAR(32) NOT NULL PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created BIGINT NOT NULL,
    last_online BIGINT NOT NULL,
    verified BIT DEFAULT '0'
);

/* admin user */
INSERT INTO users SELECT 
    '{'0' * 32}', 
    '{environ['REELS_ADMIN_USERNAME']}', 
    '{environ['REELS_ADMIN_PASSWORD']}',
    '{environ['REELS_ADMIN_EMAIL']}',
    0,
    0,
    '1'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE user_id = '{'0' * 32}'
);

/* videos */
CREATE TABLE IF NOT EXISTS videos (
    video_id CHAR(32) NOT NULL PRIMARY KEY,
    user_id CHAR(32) NOT NULL,
    session_key CHAR(32),
    file_type VARCHAR(255) NOT NULL,
    config JSON NOT NULL,
    created BIGINT NOT NULL,
    available BIT DEFAULT '0',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (session_key) REFERENCES django_session(session_key) ON DELETE SET NULL
);

/* sessionclips */
CREATE TABLE IF NOT EXISTS sessionclips (
    clip_id CHAR(32) NOT NULL PRIMARY KEY,
    session_key CHAR(32) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    config JSON NOT NULL,
    available BIT DEFAULT '0',
    FOREIGN KEY (session_key) REFERENCES django_session(session_key) ON DELETE CASCADE
);

/* sessionaudio */
CREATE TABLE IF NOT EXISTS sessionaudio (
    audio_id CHAR(32) NOT NULL PRIMARY KEY,
    session_key CHAR(32) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    config JSON NOT NULL,
    available BIT DEFAULT '0',
    FOREIGN KEY (session_key) REFERENCES django_session(session_key) ON DELETE CASCADE
);

/* posts */
CREATE TABLE IF NOT EXISTS posts (
    post_id CHAR(32) NOT NULL PRIMARY KEY,
    video_id CHAR(32) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created BIGINT NOT NULL,
    likes INT NOT NULL DEFAULT 0,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

/* likes */
CREATE TABLE IF NOT EXISTS likes (
    user_id CHAR(32) NOT NULL,
    post_id CHAR(32) NOT NULL,
    Timestamp BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

/* Tags */
CREATE TABLE IF NOT EXISTS tags (
    Name VARCHAR(225) NOT NULL,
    post_id CHAR(32) NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);""")

            # Post <--> likes coordination
            cursor.execute("""
/* MANAGE LIKES COUNT ON POSTS -- UPDATE/INSERT */
/* Drop trigger if exists */
DROP TRIGGER IF EXISTS update_post_trigger_insert ON likes;
/* Drop function if exists*/
DROP FUNCTION IF EXISTS update_post_function_insert;

/* Create/Recreate function */
CREATE FUNCTION update_post_function_insert() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE posts
    SET likes = COALESCE((SELECT COUNT(likes.user_id) FROM likes WHERE likes.post_id = NEW.post_id GROUP BY post_id), 0)
    WHERE posts.post_id = NEW.post_id;
    RETURN NEW;
END;
$$;
/* Trigger for updating liked posts in rows of posts -- Update and Insert */
CREATE TRIGGER update_post_trigger_insert
    AFTER UPDATE OR INSERT ON likes
    EXECUTE PROCEDURE update_post_function_insert();

/* MANAGE LIKES COUNT ON POSTS -- INSERT */

/* Drop trigger if exists */
DROP TRIGGER IF EXISTS update_post_trigger_delete ON likes;
/* Drop Function */
DROP FUNCTION IF EXISTS update_post_function_delete;

/* Create/Recreate function */
CREATE FUNCTION update_post_function_delete() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE posts
    SET likes = COALESCE((SELECT COUNT(likes.user_id) FROM likes WHERE likes.post_id = OLD.post_id GROUP BY post_id), 0)
    WHERE posts.post_id = OLD.post_id;
    RETURN NEW;
END;
$$;
/* Trigger for updating liked posts in rows of posts -- Update and Insert */
CREATE TRIGGER update_post_trigger_delete
    AFTER UPDATE OR INSERT ON likes
    EXECUTE PROCEDURE update_post_function_delete();""")

    # === USERS ===

    # Inserts the user into the database
    @overrides
    def insert_user(self, user: User) -> None:
        with connection.cursor() as cursor:
            query = "INSERT INTO users " \
                    "(user_id, user_name, password, email, created, last_online) " \
                    "VALUES (" \
                    f"'{user.user_id}', " \
                    f"'{user.user_name}', " \
                    f"'{user.password}', " \
                    f"'{user.email}', " \
                    f"{int(user.created)}, " \
                    f"{int(user.last_online)}, " \
                    "'0')"
            cursor.execute(query)

    @overrides
    def update_user(self, user: User):
        with connection.cursor() as cursor:
            query = f"UPDATE users " \
                    f"(" \
                    f"user_name = '{user.user_name}'" \
                    f"password = '{user.password}', " \
                    f"email = '{user.email}', " \
                    f"created = '{int(user.created)}', " \
                    f"last_online = '{int(user.last_online)}', " \
                    f"verified = '{int(user.verified)}'" \
                    f" " \
                    f"WHERE user_id = '{user.user_id}'"
            cursor.execute(query)

    # Delete user information from database
    @overrides
    def delete_user(self, user_id: str) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM users WHERE user_id = '{user_id}'"
            cursor.execute(query)

    # Get a User object from data from the database using the user_id
    @overrides
    def get_user(self, user_id: str) -> Union[User, None]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"user_id," \
                    f"user_name," \
                    f"password," \
                    f"email," \
                    f"created," \
                    f"last_online," \
                    f"verified" \
                    f" " \
                    f"FROM users WHERE user_id = '{user_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return User(user_id=row[0],
                        user_name=row[1],
                        password=row[2],
                        email=row[3],
                        created=row[4],
                        last_online=row[5],
                        verified=row[6])
        return None

    # Gets a User object from data from the database using either the username or email
    @overrides
    def get_user_by_credential(self, username_or_email: str) -> Optional[User]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"user_id," \
                    f"user_name," \
                    f"password," \
                    f"email," \
                    f"created," \
                    f"last_online," \
                    f"verified" \
                    f" " \
                    f"FROM users WHERE user_name = '{username_or_email}' OR email = '{username_or_email}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return User(user_id=row[0],
                        user_name=row[1],
                        password=row[2],
                        email=row[3],
                        created=row[4],
                        last_online=row[5],
                        verified=row[6])
        return None

    # === VIDEOS AND TAGS ===

    # Inserts video information to relational database. This does not do anything with the actual video.
    @overrides
    def insert_video(self, video: Video) -> None:
        with connection.cursor() as cursor:
            query = f"INSERT INTO videos " \
                    f"(video_id, user_id, session_key, file_type, config, created) " \
                    f"VALUES (" \
                    f"'{video.video_id}', " \
                    f"'{video.user_id}', " \
                    f"'{video.session_key}', " \
                    f"'{video.file_type}', " \
                    f"'{video.config}', " \
                    f"'{video.created}')"
            cursor.execute(query)

    @overrides
    def update_video(self, video: Video):
        with connection.cursor() as cursor:
            query = f"UPDATE videos " \
                    f"(" \
                    f"user_id = '{video.user_id}', " \
                    f"session_key = '{video.session_key}'" \
                    f"file_type = '{video.file_type}', " \
                    f"config = '{video.config}', " \
                    f"created = '{video.created}', " \
                    f"available = '{int(video.available)}', " \
                    f") " \
                    f"WHERE video_id = '{video.video_id}'"
            cursor.execute(query)

    # Deletes video information from relational database. This does not do anything with the actual video.
    @overrides
    def delete_video(self, video_id: str) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM videos WHERE video_id = '{video_id}'"
            cursor.execute(query)

    # Gets video information if it exists. If it doesn't exist, return None
    @overrides
    def get_video(self, video_id: str) -> Optional[Video]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"user_id, " \
                    f"file_type, " \
                    f"session_key, " \
                    f"video_id, " \
                    f"config, " \
                    f"created, " \
                    f"available" \
                    f" " \
                    f"FROM videos WHERE video_id = '{video_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            # TODO need to do something special with this JSON config
            return Video(user_id=row[0],
                         file_type=row[1],
                         session_key=row[2],
                         video_id=row[3],
                         config=row[4],
                         created=row[5],
                         available=bool(row[6]))
        return None

    @overrides
    def get_videos_by_user_id(self, user_id: str) -> List[Video]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"user_id, " \
                    f"file_type, " \
                    f"session_key, " \
                    f"video_id, " \
                    f"config, " \
                    f"created, " \
                    f"available" \
                    f" " \
                    f"FROM videos WHERE user_id = '{user_id}'"
            cursor.execute(query)
            rows = cursor.fetchall()
        # TODO need to do something special with this JSON config
        return [Video(user_id=row[0],
                      file_type=row[1],
                      session_key=row[2],
                      video_id=row[3],
                      config=row[4],
                      created=row[5],
                      available=bool(row[6])) for row in rows]

    @overrides
    def get_videos_by_session_key(self, session_key: str) -> List[Video]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"user_id, " \
                    f"file_type, " \
                    f"session_key, " \
                    f"video_id, " \
                    f"config, " \
                    f"created, " \
                    f"available" \
                    f" " \
                    f"FROM videos WHERE session_key = '{session_key}'"
            cursor.execute(query)
            rows = cursor.fetchall()
        # TODO need to do something special with this JSON config
        return [Video(user_id=row[0],
                      file_type=row[1],
                      session_key=row[2],
                      video_id=row[3],
                      config=row[4],
                      created=row[5],
                      available=bool(row[6])) for row in rows]

    # === SESSION ===

    # Inserts a clip uploaded from a session. This does not do anything with the actual clip.
    @overrides
    def insert_session_clip(self, clip: SessionClip) -> None:
        with connection.cursor() as cursor:
            query = f"INSERT INTO sessionclips " \
                    f"(clip_id, session_key, file_name, config) " \
                    f"VALUES (" \
                    f"'{clip.clip_id}', " \
                    f"'{clip.session_key}', " \
                    f"'{clip.file_name}', " \
                    f"'{clip.config}')"
            cursor.execute(query)

    # Deletes clip information from relational database. This does not do anything with the actual clip.
    @overrides
    def delete_session_clip(self, clip_id: str) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM sessionclips WHERE clip_id = '{clip_id}'"
            cursor.execute(query)

    # Delete all video information associated with a session. This does not do anything with the actual clip.
    @overrides
    def delete_session_clips_by_session_key(self, session_key: str):
        with connection.cursor() as cursor:
            query = f"DELETE FROM sessionclips WHERE session_key = '{session_key}'"
            cursor.execute(query)

    # Gets session clip information from a single clip id
    @overrides
    def get_session_clip(self, clip_id: str) -> Optional[SessionClip]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"clip_id, " \
                    f"session_key," \
                    f"file_name, " \
                    f"config," \
                    f"available" \
                    f" " \
                    f"FROM sessionclips WHERE clip_id = '{clip_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return SessionClip(clip_id=row[0],
                               session_key=row[1],
                               file_name=row[2],
                               config=row[3],
                               available=bool(row[4]))
        return None

    # Gets all session clip information from a single session id
    @overrides
    def get_session_clips_by_session_key(self, session_key: str) -> List[SessionClip]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"clip_id, " \
                    f"session_key," \
                    f"file_name, " \
                    f"config," \
                    f"available" \
                    f" " \
                    f"FROM sessionclips WHERE session_key = '{session_key}'"
            cursor.execute(query)
            rows = cursor.fetchall()
        return [SessionClip(clip_id=row[0],
                            session_key=row[1],
                            file_name=row[2],
                            config=row[3],
                            available=bool(row[4])) for row in rows]

    # Inserts a clip uploaded from a session. This does not do anything with the actual clip.
    @overrides
    def insert_session_audio(self, audio: SessionAudio) -> None:
        with connection.cursor() as cursor:
            query = f"INSERT INTO sessionaudio " \
                    f"(audio_id, session_key, file_name, config) " \
                    f"VALUES (" \
                    f"'{audio.audio_id}', " \
                    f"'{audio.session_key}', " \
                    f"'{audio.file_name}', " \
                    f"'{audio.config}')"
            cursor.execute(query)

    # Deletes clip information from relational database. This does not do anything with the actual clip.
    @overrides
    def delete_session_audio(self, audio_id: str) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM sessionaudio WHERE audio_id = '{audio_id}'"
            cursor.execute(query)

    # Delete all video information associated with a session. This does not do anything with the actual clip.
    @overrides
    def delete_session_audio_by_session_key(self, session_key: str):
        with connection.cursor() as cursor:
            query = f"DELETE FROM sessionaudio WHERE session_key = '{session_key}'"
            cursor.execute(query)

    # Gets session clip information from a single clip id
    @overrides
    def get_session_audio(self, audio_id: str) -> Union[SessionAudio, None]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"audio_id," \
                    f"session_key," \
                    f"file_name," \
                    f"config, " \
                    f"available" \
                    f" " \
                    f"FROM sessionaudio WHERE audio_id = '{audio_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return SessionAudio(audio_id=row[0],
                                session_key=row[1],
                                file_name=row[2],
                                config=row[3],
                                available=row[4])
        return None

    # Gets all session clip information from a single session id
    @overrides
    def get_session_audio_by_session_key(self, session_key: str) -> List[SessionAudio]:
        with connection.cursor() as cursor:
            query = f"SELECT " \
                    f"audio_id," \
                    f"session_key," \
                    f"file_name," \
                    f"config, " \
                    f"available" \
                    f" " \
                    f"FROM sessionaudio WHERE session_key = '{session_key}'"
            cursor.execute(query)
            rows = cursor.fetchall()
        return [SessionAudio(audio_id=row[0],
                             session_key=row[1],
                             file_name=row[2],
                             config=row[3],
                             available=row[4]) for row in rows]

    # === POSTS, TAGS, AND LIKES ===

    # Inserts a post to database, assuming the corresponding video information has already been inserted
    @overrides
    def insert_post(self, post: Post) -> None:
        with connection.cursor() as cursor:
            query = "INSERT INTO posts " \
                    "(post_id, video_id, title, description) " \
                    "VALUES (" \
                    f"'{post.post_id}', " \
                    f"'{post.video_id}', " \
                    f"'{self.escape_apostrophes(post.title)}', " \
                    f"'{self.escape_apostrophes(post.description)}', " \
                    f"'{post.created}', " \
                    f"0) "
            cursor.execute(query)

    # Deletes a post from database
    @overrides
    def delete_post(self, post_id: str) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM posts WHERE post_id = '{post_id}'"
            cursor.execute(query)

    # Updates a post
    @overrides
    def update_post(self, post_id: str, title: str, description: str) -> None:
        with connection.cursor() as cursor:
            query = "UPDATE posts SET " \
                    f"title='{self.escape_apostrophes(title)}', description='{self.escape_apostrophes(description)}' " \
                    f"WHERE post_id='{post_id}'"
            cursor.execute(query)

    # Gets a post from database
    @overrides
    def get_post(self, post_id: str) -> Optional[Post]:
        with connection.cursor() as cursor:
            # TODO write post column order explicitly
            query = f"SELECT * FROM posts WHERE post_id = '{post_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if row:
            return Post(row[1], row[2], row[3], row[0], row[4], row[5])
        return None

    # Get all posts owned by a user
    @overrides
    def get_post_ids_by_user_id(self, user_id: str) -> list:
        with connection.cursor() as cursor:
            query = f"SELECT posts.post_id FROM posts " \
                    f"INNER JOIN videos ON posts.video_id = videos.video_id " \
                    f"WHERE videos.user_id = '{user_id}'"
            cursor.execute(query)
            rows = cursor.fetchall()
        return [row[0] for row in rows]

    # Gets all post_id's, ordered most recent first
    @overrides
    def get_all_post_ids(self) -> list:
        # TODO trim this function to only include a subset of all posts somehow
        with connection.cursor() as cursor:
            query = "SELECT post_id FROM posts ORDER BY created DESC"
            cursor.execute(query)
            postsdb = cursor.fetchall()

        if postsdb:
            postids = []
            for pdb in postsdb:
                postids.append(pdb[0])

            return postids

        return []

    # Adds a tag to a video. Forces tag to be lowercase
    @overrides
    def add_tag(self, post_tag: PostTag) -> None:
        with connection.cursor() as cursor:
            query = f"INSERT INTO tags VALUES ('{post_tag.tag_name.lower()}', '{post_tag.post_id}')"
            cursor.execute(query)

    # Removes a tag from a video.
    @overrides
    def remove_tag(self, post_tag: PostTag) -> None:
        with connection.cursor() as cursor:
            query = f"DELETE FROM tags WHERE name = '{post_tag.tag_name.lower()}' AND post_id = '{post_tag.post_id}'"
            cursor.execute(query)

    # Returns whether a video has a video has a like on it
    @overrides
    def has_liked(self, user_id: str, post_id: str) -> bool:
        with connection.cursor() as cursor:
            # TODO write select column order explicitly
            query = f"SELECT * FROM likes WHERE user_id = '{user_id}' AND post_id = '{post_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        return bool(row)

    # Toggles a like on a video, returns new like status
    @overrides
    def toggle_like(self, user_id: str, post_id: str) -> bool:
        print(user_id)
        print(post_id)
        if self.has_liked(user_id, post_id):
            query = f"DELETE FROM likes WHERE user_id = '{user_id}' AND post_id = '{post_id}'"
            now_liked = False
        else:
            like = Like(user_id, post_id)
            query = f"INSERT INTO likes " \
                    f"(user_id, post_id, timestamp) " \
                    f"VALUES (" \
                    f"'{like.user_id}', " \
                    f"'{like.post_id}', " \
                    f"{like.timestamp})"
            now_liked = True
        with connection.cursor() as cursor:
            cursor.execute(query)
        return now_liked

    # Return number of likes on a video
    @overrides
    def likes_count(self, post_id: str) -> int:
        with connection.cursor() as cursor:
            query = f"SELECT likes FROM posts WHERE post_id = '{post_id}'"
            cursor.execute(query)
            row = cursor.fetchone()
        return int(row[0])

    # Get admin user, which is also the user which owns all
    @overrides
    def get_admin_user(self) -> User:
        with connection.cursor() as cursor:
            # TODO select user column order explicitly
            query = f"SELECT * FROM users WHERE user_id = '{'0' * 32}'"
            cursor.execute(query)
            row = cursor.fetchone()
        if not row:
            raise SystemError('There is no admin user in the database')
        return User(row[1], row[2], row[3], row[0], row[4], row[5], row[6])

    @overrides
    def escape_apostrophes(self, s: str) -> str:
        return s.replace('\'', '\'\'')

    # AGGREGATES AND SEQUENCES

    @overrides
    def get_users_post_count(self) -> list:
        with connection.cursor() as cursor:
            query = """
SELECT videos.user_id, COUNT(post_id) as post_count
FROM videos JOIN posts ON posts.video_id = videos.video_id
GROUP BY videos.user_id
ORDER BY post_count DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
        return rows

    @overrides
    def tear_down_database(self) -> None:
        if input("""
    Are you sure you want to reset the entire database?
    This will delete all data and you will have to run init_database to reinitialize.
    Type "yes" to continue, or something else to exit.
    Answer: """).lower() == 'yes':
            with connection.cursor() as cursor:
                cursor.execute("""
DROP TRIGGER IF EXISTS update_post_trigger_insert ON likes;
DROP FUNCTION IF EXISTS update_post_function_insert;
DROP TRIGGER IF EXISTS update_post_trigger_delete ON likes;
DROP FUNCTION IF EXISTS update_post_function_delete;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS sessionaudio;
DROP TABLE IF EXISTS sessionclips;
DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS users;""")
                print('Database torn down')
