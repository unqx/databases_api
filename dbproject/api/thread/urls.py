from django.conf.urls import url
import views

urlpatterns = [
    url(r'^create/', views.thread_create, name='thread_create'),
    url(r'^subscribe/', views.thread_subscribe, name='thread_subscribe'),
    url(r'^unsubscribe/', views.thread_unsubscribe, name='thread_unsubscribe'),
    url(r'^details/', views.thread_details, name='thread_details'),
    url(r'^close/', views.thread_close, name='thread_close'),
    url(r'^open/', views.thread_open, name='thread_open'),
    url(r'^remove/', views.thread_remove, name='thread_remove'),
    url(r'^restore/', views.thread_restore, name='thread_restore'),
    url(r'^update/', views.thread_update, name='thread_update'),
    url(r'^vote/', views.thread_vote, name='thread_vote'),
    url(r'^list/', views.thread_list, name='thread_list'),
    url(r'^listPosts/', views.thread_list_posts, name='thread_list_posts'),
]
