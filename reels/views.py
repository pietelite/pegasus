from django.shortcuts import render
from django.http import HttpResponse
from .sql import insert_user
from .validators import valid_username_string, valid_credentials


# Handles requests relating to login.html
def login(request) -> HttpResponse:
    # TODO implement
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    context = {}

    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            username_errors = valid_username_string(request.POST['username'])
            login_errors = valid_credentials(request.POST['username'], request.POST['password'])
            if username_errors:
                context['username_errors'] = username_errors
                request.session.set_test_cookie()
                return HttpResponse(render(request, 'reels/login.html', context))
            elif login_errors:
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
    # TODO implement
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    # if GET request, send rendered HttpResponse template
    # if POST request, register the user
    #   if register is invalid, send rendered HttpResponse with failure
    #   if register is valid, send user to social

    context = {}

    if request.method == 'POST':
        # TODO implement
        return HttpResponse(render(request, 'reels/create.html', context))

    # GET
    request.session.set_test_cookie()
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
        # TODO implement
        return HttpResponse(render(request, 'reels/forgot.html', context))

    # GET
    request.session.set_test_cookie()
    return HttpResponse(render(request, 'reels/forgot.html', context))


# Handles requests relating to create.html
def create(request) -> HttpResponse:
    # TODO implement
    # if GET request, send rendered HttpResponse template
    # if POST request
    #   if uploading, put uploaded data into memory (is it done through POST?)
    #   if done, stitch video (call algorithms), then return video

    context = {}
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
