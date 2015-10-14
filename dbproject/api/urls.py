from django.conf.urls import url, include

urlpatterns = [
    url(r'^forum/', include('dbproject.api.forum.urls')),
]