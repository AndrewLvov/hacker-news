from django.db import models


class Story(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=256)
    content = models.TextField()
