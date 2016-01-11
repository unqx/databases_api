from django.db import models
from dbproject.forum.models import Forum
from dbproject.users.models import User


class Thread(models.Model):
    forum_id = models.IntegerField(db_index=True)
    title = models.CharField(max_length=60)
    is_closed = models.BooleanField(default=False)
    user_id = models.IntegerField()
    date = models.DateTimeField(auto_now=True)
    message = models.TextField(max_length=1000)
    slug = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)
    subscribed = models.ManyToManyField(User, db_table='subscriptions')

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    posts = models.IntegerField(default=0)

    class Meta:
        db_table = 'thread'
