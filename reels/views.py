from django.shortcuts import render
from django.http import HttpResponse

# Handles requests relating to login.html
def login(request) -> HttpResponse:
    # TODO implement
    # Might be useful:
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/#examples

    # if GET request, send rendered HttpResponse template
    # if POST request, login the user
    #   if login is invalid, send rendered HttpResponse with failure
    #   if login is valid, send user to social

    context = {}
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
    return HttpResponse(render(request, 'reels/register.html', context))

# Handles requests relating to forgot.html
def forgot(request) -> HttpResponse:
    # TODO implement

    # if GET request, send rendered HttpResponse template
    # if POST request, send the user a forgot password link
    #   if information is invalid, send rendered HttpResponse with failure
    #   if information is success, send rendered HttpResponse to prompt checking email

    context = {}
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
