from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=50, null=True)
    about = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=0)
    user_follow = models.ManyToManyField("self", blank=False)

    class Meta:
        db_table = 'user'
