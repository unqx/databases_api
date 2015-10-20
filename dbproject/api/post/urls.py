from django.conf.urls import url
import views

urlpatterns = [
    url(r'^create/', views.post_create, name='post_create'),
    url(r'^details/', views.post_details, name='forum_details'),
    url(r'^remove/', views.post_remove, name='post_remove'),
    url(r'^restore/', views.post_restore, name='post_restore'),
    url(r'^vote/', views.post_vote, name='post_vote'),
    url(r'^update/', views.post_update, name='post_update'),
    url(r'^list/', views.post_list, name='post_list'),
]
