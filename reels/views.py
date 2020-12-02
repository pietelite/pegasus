import json
import time
from json import JSONDecodeError

import requests
from datetime import datetime
from django.http.response import HttpResponseBase
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, StreamingHttpResponse

from reels.azure.blob import get_blob_stream_url
from reels.config import SUPPORTED_VIDEO_TYPES, SUPPORTED_AUDIO_TYPES
from reels.models import Post
from reels.session import session_login, update_session_in_context, session_logout, \
    upload_session_audio
from reels.tasks import delete_session_clip, delete_session_audio, compile_video
from reels.models import User
from reels.session import upload_session_clips, session_is_logged_in, session_get_user
from reels.util import is_file_supported
from reels.validators import valid_email, valid_username, valid_password, \
    correct_credentials, existing_user
from reels.email import send_recovery_email
from reels.data import get_sql_handler, delete_video


def _http_response_message(request: HttpRequest, context: dict, title: str, header: str, content: str) -> HttpResponse:
    context['message_title'] = title
    context['message_header'] = header
    context['message_content'] = content
    return HttpResponse(render(request, 'reels/message.html', context))


def _unimplemented_response(request: HttpRequest, context: dict) -> HttpResponse:
    return _http_response_message(request, context,
                                  'Not Built',
                                  'Sorry! &#128533',
                                  'This page hasn\'t been built yet! Come check it out later.')


def _error_response(request: HttpRequest, context: dict) -> HttpResponse:
    return _http_response_message(request, context,
                                  'Error',
                                  'Oops! &#128534',
                                  'An error has occurred. Sorry for the trouble!')


def _not_found_response(request: HttpRequest, context: dict) -> HttpResponse:
    return _http_response_message(request, context,
                                  'Not Found',
                                  'Uh oh!',
                                  'We couldn\'t find this page for you. &#128546')


# Redirects to create page
def home(request) -> HttpResponse:
    context = {}
    update_session_in_context(context, request.session)
    return HttpResponse(render(request, 'reels/home.html', context))


# Handles requests relating to login.html
def login(request) -> HttpResponse:
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    context = {}
    update_session_in_context(context, request.session)

    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            login_errors = correct_credentials(request.POST['username'], request.POST['password'])
            if login_errors:
                context['login_errors'] = ['Something\'s not right']
                request.session.set_test_cookie()
                return HttpResponse(render(request, 'reels/login.html', context))
            else:
                session_login(request.session, get_sql_handler().get_user_by_credential(request.POST['username']))
                return HttpResponseRedirect('/create')
        else:
            context['submit_errors'] = ['Please enable cookies and try again']
            return HttpResponse(render(request, 'reels/login.html', context))

    # GET
    request.session.set_test_cookie()
    return HttpResponse(render(request, 'reels/login.html', context))


# Handles request relating to logout.html
def logout(request) -> HttpResponse:
    context = {}
    update_session_in_context(context, request.session)

    if request.method == 'GET':
        if session_is_logged_in(request.session):
            session_logout(request.session)
        update_session_in_context(context, request.session)
        return HttpResponse(render(request, 'reels/logout.html', context))
    else:
        return _error_response(request, context)


# Handles requests relating to register.html
def register(request) -> HttpResponse:
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    # if GET request, send rendered HttpResponse template
    # if POST request, register the user
    #   if register is invalid, send rendered HttpResponse with failure
    #   if register is valid, send user to social

    context = {}
    update_session_in_context(context, request.session)

    if request.method == 'POST':
        # Add errors
        context['email_errors'] = valid_email(request.POST['email'])
        if get_sql_handler().get_user_by_credential(request.POST['email']):
            context['email_errors'].append('That email already exists')
        context['username_errors'] = valid_username(request.POST['username'])
        if get_sql_handler().get_user_by_credential(request.POST['username']):
            context['username_errors'].append('That username already exists')
        context['password_errors'] = valid_password(request.POST['password'])

        if context['email_errors'] or context['username_errors'] or context['password_errors']:
            request.session.set_test_cookie()
            return HttpResponse(render(request, 'reels/register.html', context))
        else:
            get_sql_handler().insert_user(User(request.POST['username'],
                                               request.POST['password'],
                                               request.POST['email']))

            update_session_in_context(context, request.session)
            return HttpResponse(render(request, 'reels/registered.html', context))

    # GET
    return HttpResponse(render(request, 'reels/register.html', context))


# Handles requests relating to forgot.html
def forgot(request) -> HttpResponse:
    # TODO implement

    # if GET request, send rendered HttpResponse template
    # if POST request, send the user a forgot password link
    #   if information is invalid, send rendered HttpResponse with failure
    #   if information is success, send rendered HttpResponse to prompt checking email

    context = {}
    update_session_in_context(context, request.session)

    if request.method == 'POST':
        context['username_errors'] = existing_user(request.POST['username'])
        if context['username_errors']:
            return HttpResponse(render(request, 'reels/forgot.html', context))
        else:
            send_recovery_email(get_sql_handler().get_user_by_credential)
            return HttpResponse(render(request, 'reels/forgotten.html', context))

    # GET
    return HttpResponse(render(request, 'reels/forgot.html', context))


# Handles requests relating to profile.html
def profile(request) -> HttpResponse:
    if not session_is_logged_in(request.session):
        return HttpResponseRedirect('/login')

    context = {}
    update_session_in_context(context, request.session)

    if request.method == 'GET':
        request.session.set_test_cookie()
        return HttpResponse(render(request, 'reels/profile.html', context))
    elif request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            if 'delete_profile' in request.POST:
                get_sql_handler().delete_user(session_get_user(request.session).user_id)
                session_logout(request.session)

                update_session_in_context(context, request.session)
                return _http_response_message(request, context,
                                              'Deleted',
                                              'Your profile was deleted!',
                                              '')
    else:
        return _error_response(request, context)


# Handles requests relating to create.html
def create(request) -> HttpResponse:
    context = {}
    update_session_in_context(context, request.session)
    post_errors = []

    if request.method == 'GET':
        pass  # Nothing needed here

    elif request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

            if 'delete_video' in request.POST:
                delete_video_id = request.POST['delete_video']
                vid = get_sql_handler().get_video(delete_video_id)
                if vid:
                    if vid.session_key == request.session.session_key:
                        delete_video(vid.video_id, sync=True)
                    else:
                        post_errors.append('You tried to delete a video that doesn\'t belong to you!')
                else:
                    post_errors.append('We can\'t find that video')

            elif 'delete_clip' in request.POST:
                delete_clip_id = request.POST['delete_clip']
                session_clip = get_sql_handler().get_session_clip(delete_clip_id)
                if session_clip:
                    if session_clip.session_key == request.session.session_key:
                        delete_session_clip(session_clip.clip_id, sync=True)
                    else:
                        post_errors.append('You tried to delete a clip that doesn\'t belong to you!')
                else:
                    post_errors.append('We can\'t find that clip')

            elif 'delete_audio' in request.POST:
                delete_audio_id = request.POST['delete_audio']
                session_audio = get_sql_handler().get_session_audio(delete_audio_id)
                if session_audio:
                    if session_audio.session_key == request.session.session_key:
                        get_sql_handler().delete_session_audio(session_audio.audio_id)
                        delete_session_audio(session_audio.audio_id, sync=True)
                    else:
                        post_errors.append('You tried to delete audio that doesn\'t belong to you!')
                else:
                    post_errors.append('We can\'t find that audio file')

            elif request.FILES:
                # === User is uploading files ===

                # Check for video files
                video_files = []
                unsupported_file = False
                for file in request.FILES.getlist('video_file'):
                    if is_file_supported(file.name, SUPPORTED_VIDEO_TYPES):
                        video_files.append(file)
                    else:
                        unsupported_file = True
                        post_errors.append(f'File f{file.name} could not be added')
                if unsupported_file:
                    post_errors.append(
                        f'At the moment, we can only support '
                        f'the following video types: {",".join(SUPPORTED_VIDEO_TYPES)}')

                if video_files:
                    upload_session_clips(request.session.session_key, video_files)

                # Check for audio file (only one)
                if 'audio_file' in request.FILES:
                    file = request.FILES['audio_file']
                    if is_file_supported(file.name, SUPPORTED_AUDIO_TYPES):
                        upload_session_audio(request.session.session_key, request.FILES['audio_file'])
                    else:
                        post_errors.append(f'File f{file.name} could not be added')
                        post_errors.append(
                            f'At the moment, we can only support '
                            f'the following video types: {",".join(SUPPORTED_VIDEO_TYPES)}')

            else:
                # === User is compiling ===
                session_clips = get_sql_handler().get_session_clips_by_session_key(request.session.session_key)
                session_audio = get_sql_handler().get_session_audio_by_session_key(request.session.session_key)
                if not session_clips:
                    post_errors.append(f'You need to upload your clips first!')

                unavailable_files = False
                for session_clip in session_clips:
                    if not session_clip.available:
                        unavailable_files = True
                for session_aud in session_audio:
                    if not session_aud.available:
                        unavailable_files = True
                if unavailable_files:
                    post_errors.append(f'Some files are still processing!')

                config = {}
                try:
                    config = json.loads(request.POST['config_json'])
                except JSONDecodeError:
                    post_errors.append('Your configuration is not in JSON format')

                if 'file_type' not in config:
                    post_errors.append('You must specify an output file type in your configuration!')
                else:
                    if not config['file_type'] == 'mp4':
                        post_errors.append('We only support mp4 output at this time')

                # If there haven't been any errors, go ahead and compile the video
                if not post_errors:
                    compile_video(request.session, config)

        else:
            context['enable_cookies'] = True

    else:
        return _error_response(request, context)

    context['post_errors'] = post_errors
    update_session_in_context(context, request.session)
    request.session.set_test_cookie()
    return HttpResponse(render(request, 'reels/create.html', context))


# Handles requests to create or edit a post
def post_creation(request) -> HttpResponse:
    # TODO implement
    # if GET request, send rendered HttpResponse template
    # if POST request, insert/update post, then redirect to /social
    if not session_is_logged_in(request.session):
        return HttpResponseRedirect('/login')

    context = {}
    update_session_in_context(context, request.session)

    if request.method == 'POST':
        if bool(request.POST.get('delete_post')):
            get_sql_handler().delete_post(request.POST['post_id'])
        elif bool(request.POST.get('create_post')):
            if request.POST.get('post_id'):
                # editing post
                get_sql_handler().update_post(request.POST['post_id'],
                                              request.POST['title'],
                                              request.POST['description'])
            else:
                # creating new post
                post = Post('828743f41ded11ebad0f7c67a220d1e4', request.POST['title'], request.POST['description'])
                get_sql_handler().insert_post(post)

        # Nothing to do if "cancel" was pressed

        return HttpResponseRedirect('/social')

    if request.GET.get('post_id', False):
        context['post'] = get_sql_handler().get_post(request.GET['post_id'])

    return HttpResponse(render(request, 'reels/post_creation.html', context))


# Handles requests relating to social.html
def social(request) -> HttpResponse:
    # TODO implement
    # if GET request, send rendered HttpResponse template
    # if POST request (liked a video)
    #   if not logged in, show pop-up to ask for register/login
    #   if logged in, add 'like' to HTML element -> update database

    # TODO add something to get relevant context by page
    # https://django.cowhite.com/blog/working-with-url-get-post-parameters-in-django/
    if not session_is_logged_in(request.session):
        return HttpResponseRedirect('/login')

    context = {}
    update_session_in_context(context, request.session)

    if session_is_logged_in(request.session):
        context["user_id"] = session_get_user(request.session).user_id

        if request.method == 'POST':
            get_sql_handler().toggle_like(request.POST['user_id'], request.POST['post_id'])

        postids = get_sql_handler().get_all_post_ids()
        posts = []
        for pid in postids:
            post = get_sql_handler().get_post(pid)
            v = get_sql_handler().get_video(post.video_id)
            u = get_sql_handler().get_user(v.user_id)
            post.user_id = v.user_id
            post.username = u.user_name
            post.has_liked = get_sql_handler().has_liked(context["user_id"], post.post_id)
            posts.append(post)

        context["posts"] = posts

    return HttpResponse(render(request, 'reels/social.html', context))


# Handles request for the page which posts all information asking for development help
def improve(request) -> HttpResponse:
    context = {}
    update_session_in_context(context, request.session)
    if request.method == 'POST':
        # TODO implement -- send videos to raw blob location
        return HttpResponse(render(request, 'reels/unimplemented.html', context))
    return HttpResponse(render(request, 'reels/improve.html', context))


# Handles requests for getting the My Videos page
def my_videos(request) -> HttpResponse:
    context = {}
    update_session_in_context(context, request.session)

    if session_is_logged_in(request.session):

        if request.method == 'GET':
            pass  # nothing fancy to do here
        if request.method == 'POST':
            post_errors = []
            if 'delete_video' in request.POST:
                delete_video_id = request.POST['delete_video']
                vid = get_sql_handler().get_video(delete_video_id)
                if vid:
                    if vid.user_id == session_get_user(request.session).user_id:
                        delete_video(vid.video_id, sync=True)
                        update_session_in_context(context, request.session)
                    else:
                        post_errors.append('You tried to delete a video that doesn\'t belong to you!')
                else:
                    post_errors.append('We can\'t find that video')

                context['post_errors'] = post_errors

        return HttpResponse(render(request, 'reels/my_videos.html', context))

    else:
        return HttpResponseRedirect('/login')


# Handles requests for viewing a single video
def video(request) -> HttpResponse:
    context = {}
    update_session_in_context(context, request.session)
    if request.method == 'POST':
        if 'delete' in request.POST:
            # Delete video
            get_sql_handler().delete_video(request.POST['delete'])
        return HttpResponseRedirect('/myvideos')
    if 'id' in request.GET:
        context['video_id'] = request.GET['id']
        return HttpResponse(render(request, 'reels/video.html', context))
    else:
        return HttpResponse(render(request, 'reels/invalid.html', context))


def stream(request) -> HttpResponseBase:
    if request.method == 'POST':
        if 'download_video' in request.POST:
            video_id = request.POST['download_video']
            vid = get_sql_handler().get_video(video_id)
            if vid.session_key == request.session.session_key:
                url = get_blob_stream_url(request.POST['download_video'], 'pegasus-videos')
                r = requests.get(url, stream=True)
                resp = StreamingHttpResponse(streaming_content=r)
                resp['Content-Disposition'] = f'attachment; filename="reel-{datetime.utcnow()}.mp4"'
                return resp
    return HttpResponseRedirect('/create')


def stats(request) -> HttpResponseBase:
    context = {}
    update_session_in_context(context, request.session)

    if session_is_logged_in(request.session):

        context['users'] = [{'user_name': group[0], 'user_id': group[1], 'video_count': group[2]} for
                            group in get_sql_handler().get_users_video_count()]
        return HttpResponse(render(request, 'reels/stats.html', context))

    else:
        return HttpResponseRedirect('/login')
