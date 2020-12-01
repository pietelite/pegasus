from typing import List, Optional

from django.contrib.sessions.backends.base import SessionBase
from django.core.files import File

from reels.models import User, SessionClip, SessionAudio
from reels.video import save_session_clip, save_session_audio, delete_session_audio

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


def update_session_in_context(context: dict, session: SessionBase) -> None:
    context['user_data'] = {}
    if session_is_logged_in(session):
        context['user_data'] = session['user_data']

    context['session_clips'] = get_sql_handler().get_session_clips_by_session_key(session.session_key)
    context['session_audio'] = get_session_audio(session.session_key)
    context['compiled_videos'] = get_sql_handler().get_videos_by_session_key(session.session_key)
    context['unavailable_video'] = bool([vid for vid in context['compiled_videos'] if not vid.available])


# === Uploading ===

def _upload_file(file, destination_path):
    with open(destination_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


# Uploads a clip to media folder
def upload_session_clips(session_key: str, files: List[File]) -> List[SessionClip]:
    session_clips = []

    # Upload buffers
    for i in range(len(files)):
        session_clip = SessionClip(files[i].name, session_key, config={})
        _upload_file(files[i], session_clip.local_file_path())
        print(f"Uploaded to {session_clip.local_file_path()}")
        session_clips.append(session_clip)

    # Upload from buffer media location to blob storage
    for session_clip in session_clips:
        save_session_clip(session_clip, sync=False)

    return session_clips


# Uploads an audio file
def upload_session_audio(session_key: str, file: File) -> SessionAudio:
    # Delete a audio if it exists already
    session_audio = get_session_audio(session_key)
    if session_audio:
        delete_session_audio(session_audio.audio_id, sync=True)
    # Upload new audio
    session_audio = SessionAudio(file.name, session_key)
    _upload_file(file, session_audio.local_file_path())

    save_session_audio(session_audio, sync=False)

    return session_audio


# Gets the audio associated with a session
def get_session_audio(session_key: str) -> Optional[SessionAudio]:
    try:
        return get_sql_handler().get_session_audio_by_session_key(session_key)[0]
    except IndexError:
        return None
