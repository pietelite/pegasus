from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    re_path(r'login/?', views.login, name='login'),
    re_path(r'logout/?', views.logout, name='logout'),
    re_path(r'register/?', views.register, name='register'),
    re_path(r'forgot/?', views.forgot, name='forgot'),
    re_path(r'create/?', views.create, name='create'),
    re_path(r'social/?', views.social, name='social')
]
