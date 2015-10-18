from django.db import models

class Forum(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    owner_id = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=0)

    class Meta:
        db_table = 'forum'