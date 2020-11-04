from django.contrib.sessions.backends.base import SessionBase
from django.core.files import File

from pegasus.settings import MEDIA_ROOT, MEDIA_URL
from reels.models import User, SessionClip
import time
from os import listdir


# === Users ===

# Login a user
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


def session_context(session: SessionBase) -> dict:
    if session_is_logged_in(session):
        return {'user_data': session['user_data']}
    else:
        return {}


# === Uploading ===

# Uploads a video to media folder
def upload_session_clips(session_key: str, files: list) -> list:
    # TODO move to blob storage
    clips = []
    time_sec = int(time.time())
    for i in range(len(files)):
        destination_location = '{}reels-{}-{}-{}.{}'.format(MEDIA_ROOT, session_key, time_sec, i, 'mp4')
        with open(destination_location, 'wb+') as destination:
            for chunk in files[i].chunks():
                destination.write(chunk)
        clips.append(SessionClip(destination_location, session_key, {}))
    return clips


# Gets a list of SessionClips associated with a session
def get_session_clips(session_key: str) -> list:
    # TODO move to blob storage
    return [MEDIA_URL + f for f in listdir(MEDIA_ROOT) if f[:5] == 'reels' and f[-4:] == '.mp4']
