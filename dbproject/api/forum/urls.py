from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^create/', views.forum_create, name='forum_create'),
]