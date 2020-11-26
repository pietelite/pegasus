import re
from os.path import join
from typing import Union, List, Optional

from django.contrib.sessions.backends.base import SessionBase
from django.core.files import File
from django.core.files.storage import get_storage_class

from pegasus.settings import MEDIA_URL, MEDIA_ROOT
from reels.azure.blob import save_clip_to_blob, save_audio_to_blob, delete_clip_in_blob, delete_audio_in_blob
from reels.models import User, SessionClip, SessionAudio
import time
from os import listdir, remove

# === Users ===

# Login a user
from reels.sql.sql import get_sql_handler


def session_login(session: SessionBase, user: User) -> None:
    session['user_data'] = user.__dict__


# Logout a user
def session_logout(session: SessionBase) -> None:
    session.pop('user_data')


# Check if a user is already logged in
def session_is_logged_in(session: SessionBase) -> bool:
    return 'user_data' in session


# Get the User of a session, assuming one exists.
def session_get_user(session: SessionBase) -> User:
    d = session['user_data']
    return User(d['user_name'], d['password'], d['email'], d['user_id'],
                d['created'], d['last_online'], d['verified'])


def update_session_in_context(context: dict, session: SessionBase) -> dict:
    context['user_data'] = {}
    if session_is_logged_in(session):
        context['user_data'] = session['user_data']
    context['session_clips'] = [{'file_name': clip.file_name} for clip in
                                get_session_clips(session.session_key)]
    session_audio = get_session_audio(session.session_key)
    if session_audio:
        context['session_audio'] = {'file_name': session_audio.file_name}


# === Uploading ===

def _upload_file(file, destination_path):
    with open(destination_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


# Uploads a clip to media folder
def upload_session_clips(session_key: str, files: List[File]) -> List[SessionClip]:
    session_clips = []
    time_sec = int(time.time())

    # Upload buffers
    for i in range(len(files)):
        session_clip = SessionClip(files[i].name, session_key, preset_config={})
        _upload_file(files[i], session_clip.temp_file_path())
        session_clips.append(session_clip)

    # Upload from buffer media location to blob storage
    for clip in session_clips:
        get_sql_handler().insert_session_clip(clip)
        print("saving clip to blob")
        save_clip_to_blob(clip.temp_file_path(), clip.clip_id)
        remove(clip.temp_file_path())
    return session_clips


# Gets a list of SessionClips associated with a session
def get_session_clips(session_key: str) -> List[SessionClip]:
    return get_sql_handler().get_session_clips_by_session_key(session_key)


# Uploads an audio file
def upload_session_audio(session_key: str, file: File) -> SessionAudio:
    # Delete a audio if it exists already
    session_audio = get_session_audio(session_key)
    if session_audio:
        delete_audio_in_blob(session_audio.audio_id)
        get_sql_handler().delete_session_audio(session_audio.audio_id)
    # Upload new audio
    session_audio = SessionAudio(file.name, session_key)
    _upload_file(file, join(MEDIA_ROOT, session_audio.temp_file_path()))
    get_sql_handler().insert_session_audio(session_audio)
    save_audio_to_blob(join(MEDIA_ROOT, session_audio.temp_file_path()), session_audio.audio_id)
    remove(session_audio.temp_file_path())
    return session_audio


# Gets the audio associated with a session
def get_session_audio(session_key: str) -> Optional[SessionAudio]:
    try:
        return get_sql_handler().get_session_audio_by_session_key(session_key)[0]
    except IndexError:
        return None


# Get rid of all data from uploaded content
def clear_session_uploads(session_key: str) -> None:
    session_clips = get_session_clips(session_key)
    for session_clip in session_clips:
        delete_clip_in_blob(session_clip.clip_id)
        get_sql_handler().delete_session_clip(session_clip.clip_id)

    session_audio = get_session_audio(session_key)
    if session_audio:
        delete_audio_in_blob(session_audio.audio_id)
        get_sql_handler().delete_session_audio(session_audio.audio_id)
