from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=100)
    follows = models.JSONField(default=list, blank=True)
    notifications = models.JSONField(default=list, blank=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
