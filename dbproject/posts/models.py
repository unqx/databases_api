from django.db import models


class Post(models.Model):
    forum_id = models.IntegerField()
    thread_id = models.IntegerField(db_index=True)
    user_id = models.IntegerField(db_index=True)
    message = models.TextField(max_length=1000)
    date = models.DateTimeField()
    parent = models.IntegerField(default=None, null=True, db_index=True)
    path = models.CharField(null=True, default=None, max_length=1000)
    is_approved = models.BooleanField(default=False)
    is_highlited = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        db_table = 'post'

        index_together = [
            ['forum_id', 'user_id']
        ]