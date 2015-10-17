from django.conf.urls import url, include

urlpatterns = [
    url(r'^forum/', include('dbproject.api.forum.urls')),
    url(r'^user/', include('dbproject.api.user.urls')),
    url(r'^thread/', include('dbproject.api.thread.urls'))
]