from typing import Union, List

from django.db import connection

from reels.models import Video, Post, PostTag, User, SessionClip, SessionAudio


class SqlHandlerInterface:

    # Initialize all objects in database
    def init_database(self) -> None:
        raise NotImplementedError

    # === USERS ===

    # Inserts the user into the database
    def insert_user(self, user: User) -> None:
        raise NotImplementedError

    # Updates the user in the database with the same user_id
    def update_user(self, user: User) -> None:
        raise NotImplementedError

    # Delete user information from database
    def delete_user(self, user_id: str) -> None:
        raise NotImplementedError

    # Get a User object from data from the database using the user_id
    def get_user(self, user_id: str) -> Union[User, None]:
        raise NotImplementedError

    # Gets a User object from data from the database using either the username or email
    def get_user_by_credential(self, username_or_email: str) -> Union[User, None]:
        raise NotImplementedError

    # === VIDEOS AND TAGS ===

    # Inserts video information to relational database. This does not do anything with the actual video.
    def insert_video(self, video: Video) -> None:
        raise NotImplementedError

    # Updates the video in the database with the same video_id
    def update_video(self, video: Video) -> None:
        raise NotImplementedError

    # Deletes video information from relational database. This does not do anything with the actual video.
    def delete_video(self, video_id: str) -> None:
        raise NotImplementedError

    # Gets video information if it exists. If it doesn't exist, return None
    def get_video(self, video_id: str) -> Union[Video, None]:
        raise NotImplementedError

    # Gets all video information from a user id
    def get_videos_by_user_id(self, user_id: str) -> List[Video]:
        raise NotImplementedError

    def get_videos_by_session_key(self, session_key: str) -> List[Video]:
        raise NotImplementedError

    # === SESSION ===

    # Inserts a clip uploaded from a session. This does not do anything with the actual clip.
    def insert_session_clip(self, clip: SessionClip) -> None:
        raise NotImplementedError

    # Updates a clip uploaded from a session based on its clip_id. This does not do anything with the actual clip.
    def update_session_clip(self, clip: SessionClip) -> None:
        raise NotImplementedError

    # Deletes clip information from relational database. This does not do anything with the actual clip.
    def delete_session_clip(self, clip_id: str) -> None:
        raise NotImplementedError

    # Delete all video information associated with a session. This does not do anything with the actual clip.
    def delete_session_clips_by_session_key(self, session_key: str):
        raise NotImplementedError

    # Gets session clip information from a single clip id
    def get_session_clip(self, clip_id: str) -> Union[SessionClip, None]:
        raise NotImplementedError

    # Gets all session clip information from a single session id
    def get_session_clips_by_session_key(self, session_key: str) -> List[SessionClip]:
        raise NotImplementedError

    # Inserts audio uploaded from a session. This does not do anything with the actual audio.
    def insert_session_audio(self, audio: SessionAudio) -> None:
        raise NotImplementedError

    # Updates audio uploaded from a session. This does not do anything with the actual audio.
    def update_session_audio(self, audio: SessionAudio) -> None:
        raise NotImplementedError

    # Deletes audio information from relational database. This does not do anything with the actual audio.
    def delete_session_audio(self, audio_id: str) -> None:
        raise NotImplementedError

    # Delete all audio information associated with a session. This does not do anything with the actual audio.
    def delete_session_audio_by_session_key(self, session_key: str):
        raise NotImplementedError

    # Gets session audio information from a single audio_id
    def get_session_audio(self, audio_id: str) -> Union[SessionAudio, None]:
        raise NotImplementedError

    # Gets all session audio information from a single session_key
    def get_session_audio_by_session_key(self, session_key: str) -> List[SessionAudio]:
        raise NotImplementedError

    # === POSTS, TAGS, AND LIKES ===

    # Inserts a post to database, assuming the corresponding video information has already been inserted
    def insert_post(self, post: Post) -> None:
        raise NotImplementedError

    # Updates a post in the database using the post_id to match
    def update_post(self, post: Post) -> None:
        raise NotImplementedError

    # Deletes a post from database
    def delete_post(self, post_id: str) -> None:
        raise NotImplementedError

    # Updates a post
    def update_post(self, post_id: str, title: str, description: str) -> None:
        raise NotImplementedError

    # Gets a post from database
    def get_post(self, post_id: str) -> Union[Post, None]:
        raise NotImplementedError

    # Get all posts owned by a user
    def get_post_ids_by_user_id(self, user_id: str) -> list:
        raise NotImplementedError

    # Gets all PostId's, ordered most recent first
    def get_all_post_ids(self) -> list:
        raise NotImplementedError

    # Adds a tag to a video. Forces tag to be lowercase
    def add_tag(self, post_tag: PostTag) -> None:
        raise NotImplementedError

    # Removes a tag from a video.
    def remove_tag(self, post_tag: PostTag) -> None:
        raise NotImplementedError

    # Returns whether a video has a video has a like on it
    def has_liked(self, user_id: str, post_id: str) -> bool:
        raise NotImplementedError

    # Toggles a like on a video, returns new like status
    def toggle_like(self, user_id: str, post_id: str) -> bool:
        raise NotImplementedError

    # Return number of likes on a video
    def likes_count(self, post_id: str) -> int:
        raise NotImplementedError

    # Get admin user, which is also the user which owns all
    def get_admin_user(self) -> User:
        raise NotImplementedError

    def escape_apostrophes(self, s: str) -> str:
        raise NotImplementedError

    # AGGREGATES AND SEQUENCES

    def get_users_video_count(self) -> list:
        raise NotImplementedError

    def tear_down_database(self) -> None:
        raise NotImplementedError
