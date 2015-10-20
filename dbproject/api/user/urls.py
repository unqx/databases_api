from django.conf.urls import url
import views

urlpatterns = [
    url(r'^create/', views.user_create, name='forum_create'),
    url(r'^follow/', views.user_follow, name='user_follow'),
    url(r'^unfollow/', views.user_unfollow, name='user_unfollow'),
    url(r'^details/', views.user_details, name='user_details'),
    url(r'^listFollowers/', views.user_list_followers, name='user_list_followers'),
    url(r'^listFollowing/', views.user_list_following, name='user_list_following'),
    url(r'^updateProfile/', views.user_update_profile, name='user_update_profile'),
    url(r'^listPosts/', views.user_list_posts, name='user_list_posts'),

]