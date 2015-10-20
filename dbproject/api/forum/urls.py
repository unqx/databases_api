from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^create/', views.forum_create, name='forum_create'),
    url(r'^details/', views.forum_details, name='forum_details'),
    url(r'^listUsers/', views.forum_list_users, name='forum_list_users'),
    url(r'^listThreads/', views.forum_list_threads, name='forum_list_threads'),
    url(r'^listPosts/', views.forum_list_posts, name='forum_list_posts'),

]
