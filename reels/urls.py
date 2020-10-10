from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.social, name='social'),
    path('register/', views.login, name='register'),
    path('login/', views.login, name='login'),
    path('create/', views.create, name='create'),
    path('social/', views.social, name='social')
]
