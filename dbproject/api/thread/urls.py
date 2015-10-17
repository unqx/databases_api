from django.conf.urls import url
import views

urlpatterns = [
    url(r'^create/', views.thread_create, name='thread_create'),
]