from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.social, name='social'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('forgot/', views.forgot, name='forgot'),
    path('create/', views.create, name='create'),
    path('social/', views.social, name='social')
]
