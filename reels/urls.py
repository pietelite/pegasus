from django.conf.urls.static import static
from pegasus.settings import STATIC_URL, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    re_path(r'login/?', views.login, name='login'),
    re_path(r'logout/?', views.logout, name='logout'),
    re_path(r'register/?', views.register, name='register'),
    re_path(r'forgot/?', views.forgot, name='forgot'),
    re_path(r'create/?', views.create, name='create'),
    re_path(r'social/?', views.social, name='social'),
    re_path(r'post_creation/?', views.post_creation, name='create post')
]
urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
