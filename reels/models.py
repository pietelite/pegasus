from django.db import models
import time
from uuid import UUID, uuid1

from reels.util import uuid_to_str


class User:

    def __init__(self, user_name: str, password: str, email: str, user_id=uuid_to_str(uuid1()),
                 created=int(time.time()), last_online=int(time.time()), verified=False):
        self.user_name = user_name
        self.password = password
        self.email = email
        self.user_id = user_id
        self.created = created
        self.last_online = last_online
        self.verified = verified


class Video:

    def __init__(self, user_id: str, video_id=uuid_to_str(uuid1()), created=int(time.time())):
        self.user_id = user_id
        self.video_id = video_id
        self.created = created


class Post:

    def __init__(self, video_id: str, title: str, description: str, post_id=uuid_to_str(uuid1()),
                 created=int(time.time()), likes_count=0):
        self.video_id = video_id
        self.title = title
        self.description = description
        self.post_id = post_id
        self.likes_count = likes_count
        self.created = created


class PostTag:

    def __init__(self, tag_name: str, post_id: str):
        self.tag_name = tag_name.lower()
        self.post_id = post_id


class Like:

    def __init__(self, user_id: str, post_id: str, timestamp=int(time.time())):
        self.user_id = user_id
        self.post_id = post_id
        self.timestamp = timestamp


# Class for a clip uploaded by a user
class SessionClip:

    def __init__(self, location: str, session_key: str, preset_config: dict):
        self.location = location
        self.session_key = session_key
        self.preset_config = preset_config


# Class for an audio file uploaded by a user
class SessionAudio:

    def __init__(self, location: str, session_key: str, preset_config: dict):
        self.location = location
        self.session_key = session_key
        self.preset_config = preset_config
