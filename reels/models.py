from os.path import join, exists

from django.db import models
import time
from uuid import UUID, uuid4

from pegasus.settings import MEDIA_ROOT
from reels.util import uuid_to_str, get_file_type
from moviepy.editor import VideoFileClip, AudioFileClip


class User:

    def __init__(self, user_name: str, password: str, email: str, user_id: str = None,
                 created=int(time.time()), last_online=int(time.time()), verified=False):
        if user_id is None:
            user_id = uuid_to_str(uuid4())
        self.user_name = user_name
        self.password = password
        self.email = email
        self.user_id = user_id
        self.created = created
        self.last_online = last_online
        self.verified = verified


class Video:

    def __init__(self, user_id: str, file_type: str,
                 session_key: str, video_id: str = None,
                 config: dict = None, created=int(time.time()),
                 available: bool = False):
        if config is None:
            config = {}
        if video_id is None:
            video_id = uuid_to_str(uuid4())
        self.user_id = user_id
        self.file_type = file_type
        self.session_key = session_key
        self.video_id = video_id
        self.config = config
        self.created = created
        self.available = available

    def duration(self):
        if exists(self.temp_file_path()):
            return VideoFileClip(self.temp_file_name())
        else:
            raise FileExistsError(f'The Video {self.video_id} is not saved locally')

    def temp_file_name(self):
        return f'{self.video_id}.{self.file_type}'

    def temp_file_path(self):
        return join(MEDIA_ROOT, self.temp_file_name())

    def contextualize(self):
        return {
            'user_id': self.user_id,
            'file_type': self.file_type,
            'session_key': self.session_key,
            'video_id': self.video_id,
            'config': self.config,
            'created': time.ctime(self.created)
        }


class Post:

    def __init__(self, video_id: str, title: str, description: str, post_id=uuid_to_str(uuid4()),
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

    def __init__(self, file_name: str, session_key: str,
                 clip_id: str = None, config: dict = None, available: bool = False):
        if config is None:
            config = {}
        if clip_id is None:
            clip_id = uuid_to_str(uuid4())
        self.file_name = file_name
        self.session_key = session_key
        self.clip_id = clip_id
        self.config = config
        self.available = available

    def duration(self):
        if exists(self.temp_file_path()):
            return VideoFileClip(self.temp_file_name())
        else:
            raise FileExistsError(f'The SessionClip {self.clip_id} is not saved locally')

    def temp_file_name(self):
        return f'{self.clip_id}.{get_file_type(self.file_name)}'

    def temp_file_path(self):
        return join(MEDIA_ROOT, self.temp_file_name())


# Class for an audio file uploaded by a user
class SessionAudio:

    def __init__(self, file_name: str, session_key: str,
                 audio_id: str = None, config: dict = None, available: bool = False):
        if config is None:
            config = {}
        if audio_id is None:
            audio_id = uuid_to_str(uuid4())
        self.file_name = file_name
        self.session_key = session_key
        self.audio_id = audio_id
        self.config = config
        self.available = available

    def duration(self):
        if exists(self.temp_file_path()):
            return AudioFileClip(self.temp_file_name())
        else:
            raise FileExistsError(f'The SessionAudio {self.audio_id} is not saved locally')

    def temp_file_name(self):
        return f'{self.audio_id}.{get_file_type(self.file_name)}'

    def temp_file_path(self):
        return join(MEDIA_ROOT, self.temp_file_name())
