from django.db import models
from dbproject.forum.models import Forum


class Thread(models.Model):
    forum_id = models.IntegerField()
    title = models.CharField(max_length=60)
    is_closed = models.BooleanField(default=False)
    user_id = models.IntegerField()
    date = models.DateTimeField(auto_now=True)
    message = models.TextField(max_length=1000)
    slug = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'thread'
