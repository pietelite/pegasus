import time

from django.contrib.sessions.backends.base import SessionBase
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .models import User, Post
from .session import upload_session_clips, session_login, session_context, session_logout
from .azure.sql import insert_user, get_user_by_credential, get_all_post_ids, get_post, get_video, get_user, has_liked, \
    toggle_like, delete_post, insert_post, update_post, get_videos_by_user_id, get_admin_user, tear_down_database, \
    init_database, delete_video
from .tasks import make
from .models import User
from .session import upload_session_clips, session_login, session_context, session_logout, upload_session_audio
from .azure.sql import insert_user, get_user_by_credential, get_all_post_ids, get_post, get_video, get_user, has_liked, \
    toggle_like
from .session import upload_session_clips, get_session_clips, session_is_logged_in, session_get_user
from .azure.sql import insert_user, get_user
from .validators import valid_email, valid_username, valid_password, \
    correct_credentials, existing_user
from .recover import send_recovery_email


def pegasus_context(session: SessionBase) -> dict:
    context = {}
    context = {**context, **session_context(session)}
    return context;


# Redirects to create page
def home(request) -> HttpResponse:
    return HttpResponseRedirect('/create')


# Handles requests relating to login.html
def login(request) -> HttpResponse:
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    context = pegasus_context(request.session)

    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            login_errors = correct_credentials(request.POST['username'], request.POST['password'])
            if login_errors:
                context['login_errors'] = ['Something\'s not right']
                request.session.set_test_cookie()
                return HttpResponse(render(request, 'reels/login.html', context))
            else:
                session_login(request.session, get_user_by_credential(request.POST['username']))
                return HttpResponseRedirect('/create')
        else:
            context['submit_errors'] = ['Please enable cookies and try again']
            return HttpResponse(render(request, 'reels/login.html', context))

    # GET
    request.session.set_test_cookie()
    return HttpResponse(render(request, 'reels/login.html', context))


# Handles request relating to logout.html
def logout(request) -> HttpResponse:
    # TODO make more robust

    session_logout(request.session)
    context = pegasus_context(request.session)

    # GET
    return HttpResponse(render(request, 'reels/logout.html', context))


# Handles requests relating to register.html
def register(request) -> HttpResponse:
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    # if GET request, send rendered HttpResponse template
    # if POST request, register the user
    #   if register is invalid, send rendered HttpResponse with failure
    #   if register is valid, send user to social

    context = pegasus_context(request.session)

    if request.method == 'POST':
        # Add errors
        context['email_errors'] = valid_email(request.POST['email'])
        if get_user_by_credential(request.POST['email']):
            context['email_errors'].append('That email already exists')
        context['username_errors'] = valid_username(request.POST['username'])
        if get_user_by_credential(request.POST['username']):
            context['username_errors'].append('That username already exists')
        context['password_errors'] = valid_password(request.POST['password'])

        if context['email_errors'] or context['username_errors'] or context['password_errors']:
            request.session.set_test_cookie()
            return HttpResponse(render(request, 'reels/register.html', context))
        else:
            insert_user(User(request.POST['username'], request.POST['password'], request.POST['email']))
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

    context = pegasus_context(request.session)

    if request.method == 'POST':
        context['username_errors'] = existing_user(request.POST['username'])
        if context['username_errors']:
            return HttpResponse(render(request, 'reels/forgot.html', context))
        else:
            send_recovery_email(get_user_by_credential)
            return HttpResponse(render(request, 'reels/forgotten.html', context))

    # GET
    return HttpResponse(render(request, 'reels/forgot.html', context))


# Handles requests relating to create.html
def create(request) -> HttpResponse:
    # if GET request, send rendered HttpResponse template
    # if POST request
    #   if uploading, put uploaded data into memory (is it done through POST?)
    #   if done, stitch video (call algorithms), then return video

    context = pegasus_context(request.session)
    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            if request.FILES:
                video_files = [f for f in request.FILES.getlist('video_file') if f.name[-4:] == '.mp4']
                if 'audio_file' in request.FILES and request.FILES['audio_file'].name[-4:] == '.mp3':
                    upload_session_audio(request.session.session_key, request.FILES['audio_file'])
                upload_session_clips(request.session.session_key, video_files)
                return HttpResponseRedirect('/create')
            elif 'preset' in request.POST:
                if get_session_clips(request.session.session_key):
                    # Get user info
                    if session_is_logged_in(request.session):
                        user = session_get_user(request.session)
                    else:
                        user = get_admin_user()
                    make.delay(request.session.session_key, user.user_id, request.POST['preset'])
                    return HttpResponse(render(request, 'reels/compile.html', context))
                else:
                    # TODO do something to say that videos must be uploaded
                    print('You must upload videos...')
                    return HttpResponseRedirect('/create')
            else:
                # TODO do something to say that a preset choice is required
                print('You must upload audio...')
                return HttpResponseRedirect('/create')
        else:
            # TODO print error about enabling cookies
            print('You must enable cookies...')
            return HttpResponseRedirect('/create')

    # GET
    request.session.set_test_cookie()
    return HttpResponse(render(request, 'reels/create.html', context))


# Handles requests to create or edit a post
def post_creation(request) -> HttpResponse:
    # TODO implement
    # if GET request, send rendered HttpResponse template
    # if POST request, insert/update post, then redirect to /social
    context = pegasus_context(request.session)

    if request.method == 'POST':
        if bool(request.POST.get('delete_post')):
            delete_post(request.POST['post_id'])
        elif bool(request.POST.get('create_post')):
            if request.POST.get('post_id'):
                # editing post
                update_post(request.POST['post_id'], request.POST['title'], request.POST['description'])
            else:
                # creating new post
                post = Post('828743f41ded11ebad0f7c67a220d1e4', request.POST['title'], request.POST['description'])
                insert_post(post)

        # Nothing to do if "cancel" was pressed

        return HttpResponseRedirect('/social')

    if request.GET.get('post_id', False):
        context['post'] = get_post(request.GET['post_id'])

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

    context = pegasus_context(request.session)

    if session_is_logged_in(request.session):
        context["user_id"] = session_get_user(request.session).user_id

        if request.method == 'POST':
            toggle_like(request.POST['user_id'], request.POST['post_id'])

        postids = get_all_post_ids()
        posts = []
        for pid in postids:
            post = get_post(pid)
            v = get_video(post.video_id)
            u = get_user(v.user_id)
            post.user_id = v.user_id
            post.username = u.user_name
            post.has_liked = has_liked(context["user_id"], post.post_id)
            posts.append(post)

        context["posts"] = posts

    return HttpResponse(render(request, 'reels/social.html', context))


# Handles requests for getting the My Videos page
def my_videos(request) -> HttpResponse:
    context = pegasus_context(request.session)

    if session_is_logged_in(request.session):
        videos = get_videos_by_user_id(session_get_user(request.session).user_id)
        context['user_videos'] = []
        for video in videos:
            context['user_videos'].append(
                {
                    'formatted_time': time.ctime(video.created),
                    'video_id': video.video_id,
                })
        if videos:
            context['most_recent_video'] = time.ctime((max(videos, key=lambda v: v.created)).created)
        return HttpResponse(render(request, 'reels/my_videos.html', context))
    else:
        return HttpResponse(render(request, 'reels/login.html', context))


# Handles requests for viewing a single video
def video(request) -> HttpResponse:
    context = pegasus_context(request.session)
    if request.method == 'POST':
        if 'delete' in request.POST:
            # Delete video
            delete_video(request.POST['delete'])
        return HttpResponseRedirect('/myvideos')
    if 'id' in request.GET:
        context['video_id'] = request.GET['id']
        return HttpResponse(render(request, 'reels/video.html', context))
    else:
        return HttpResponse(render(request, 'reels/invalid.html', context))