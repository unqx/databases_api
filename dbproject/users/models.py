from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    about = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=0)
    user_follow = models.ManyToManyField("self", blank=False)

    class Meta:
        db_table = 'user'
