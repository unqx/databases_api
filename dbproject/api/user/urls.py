from django.conf.urls import url
import views

urlpatterns = [
    url(r'^create/', views.user_create, name='forum_create'),
    url(r'^follow/', views.user_follow, name='user_follow'),
    url(r'^unfollow/', views.user_unfollow, name='user_unfollow'),
    url(r'^details/', views.user_details, name='user_details'),
]