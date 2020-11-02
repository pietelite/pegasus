from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .session import upload_session_clips
from .sql import insert_user, get_user
from .validators import valid_email, valid_username, valid_password, \
    correct_credentials, existing_user
from .recover import send_recovery_email


# Redirects to create page
def home(request) -> HttpResponse:
    return HttpResponseRedirect('/create')


# Handles requests relating to login.html
def login(request) -> HttpResponse:
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    context = {}

    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            login_errors = correct_credentials(request.POST['username'], request.POST['password'])
            if login_errors:
                context['login_errors'] = login_errors
                request.session.set_test_cookie()
                return HttpResponse(render(request, 'reels/login.html', context))
            else:

                return HttpResponse(render(request, 'reels/create.html', context))
        else:
            context['submit_errors'] = ['Please enable cookies and try again']
            return HttpResponse(render(request, 'reels/login.html', context))

    # GET
    request.session.set_test_cookie()
    return HttpResponse(render(request, 'reels/login.html', context))


# Handles requests relating to register.html
def register(request) -> HttpResponse:
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    # if GET request, send rendered HttpResponse template
    # if POST request, register the user
    #   if register is invalid, send rendered HttpResponse with failure
    #   if register is valid, send user to social

    context = {}

    if request.method == 'POST':
        # Add errors
        context['email_errors'] = valid_email(request.POST['email'])
        if get_user(request.POST['email']):
            context['email_errors'].append('That email already exists')
        context['username_errors'] = valid_username(request.POST['username'])
        if get_user(request.POST['username']):
            context['username_errors'].append('That username already exists')
        context['password_errors'] = valid_password(request.POST['password'])

        if context['email_errors'] or context['username_errors'] or context['password_errors']:
            request.session.set_test_cookie()
            return HttpResponse(render(request, 'reels/register.html', context))
        else:
            insert_user(request.POST['email'], request.POST['username'], request.POST['password'])
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

    if request.method == 'POST':
        context['username_errors'] = existing_user(request.POST['username'])
        if context['username_errors']:
            return HttpResponse(render(request, 'reels/forgot.html', context))
        else:
            send_recovery_email(get_user)
            return HttpResponse(render(request, 'reels/forgotten.html', context))

    # GET
    return HttpResponse(render(request, 'reels/forgot.html', context))


# Handles requests relating to create.html
def create(request) -> HttpResponse:
    # TODO implement
    # if GET request, send rendered HttpResponse template
    # if POST request
    #   if uploading, put uploaded data into memory (is it done through POST?)
    #   if done, stitch video (call algorithms), then return video

    context = {}
    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            upload_session_clips(request.session.session_key, request.FILES.getlist('file'))
            return HttpResponseRedirect('/create')
        else:
            # TODO print error about cookies
            return HttpResponse(render(request, 'reels/create.html', context))

    # GET
    request.session.set_test_cookie()
    return HttpResponse(render(request, 'reels/create.html', context))


# Handles requests relating to social.html
def social(request) -> HttpResponse:
    # TODO implement
    # if GET request, send rendered HttpResponse template
    # if POST request (liked a video)
    #   if not logged in, show pop-up to ask for register/login
    #   if logged in, add 'like' to HTML element -> update database

    context = {}
    return HttpResponse(render(request, 'reels/social.html', context))
