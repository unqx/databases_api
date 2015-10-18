from django.conf.urls import url
import views

urlpatterns = [
    url(r'^create/', views.thread_create, name='thread_create'),
    url(r'^subscribe/', views.thread_subscribe, name='thread_subscribe'),
    url(r'^unsubscribe/', views.thread_unsubscribe, name='thread_unsubscribe')
]