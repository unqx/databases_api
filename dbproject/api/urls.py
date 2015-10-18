from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^forum/', include('dbproject.api.forum.urls')),
    url(r'^user/', include('dbproject.api.user.urls')),
    url(r'^thread/', include('dbproject.api.thread.urls')),
    url(r'^clear/', views.clear, name='clear'),
    url(r'^status/', views.status, name='status')
]