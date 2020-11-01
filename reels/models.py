from django.db import models
import time
import uuid


class User:

    def __init__(self, email, user_name, password, created=time.time(), last_online=time.time()):
        self.user_id = uuid.uuid1()
        self.email = email
        self.user_name = user_name
        self.password = password
        self.created = created
        self.last_online = last_online


class Video:

    def __init__(self, user_id, file_loc, created=time.time()):
        self.video_id = uuid.uuid1()
        self.user_id = user_id
        self.file_loc = file_loc
        self.created = created


class Post:

    def __init__(self, video_id, title, description, is_public=True, num_likes=0, created=time.time()):
        self.video_id = video_id
        self.title = title
        self.description = description
        self.is_public = is_public
        self.num_likes = num_likes
        self.created = created


class VideoTag:

    def __init__(self, video_id, tag):
        self.video_id = video_id
        self.tag = tag.lower()


class Like:

    def __init__(self, user_id, post_id, timestamp=time.time()):
        self.user_id = user_id
        self.post_id = post_id
        self.timestamp = timestamp


# Class for a clip uploaded by a user
class SessionClip:

    def __init__(self, location, session_id, preset_config):
        self.clip_location = location
        self.session_id = session_id
        self.preset_config = preset_config
