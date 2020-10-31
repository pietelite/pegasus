from pegasus.settings import MEDIA_URL
import time


# Login a user
def session_login(request, user) -> None:
    request.session['user_id'] = user.user_id


# Logout a user
def session_logout(request, user) -> None:
    request.session.pop('user_id')


# Check if a user is already logged in
def session_is_logged_in(request, user) -> None:
    return request.session['user_id'] and request.session['user_id'] == user.user_id


# Uploads a video to media folder
def upload_video(request, file) -> None:
    # TODO fix
    with open('{}{}-{}.{}'.format(MEDIA_URL, request.session.session_key, time.time(), 'mp4'), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    print('Video uploaded')
