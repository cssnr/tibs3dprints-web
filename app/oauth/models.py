from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    avatar_hash = models.CharField(blank=True, max_length=255, default="")
    access_token = models.CharField(blank=True, max_length=255, default="")
    refresh_token = models.CharField(blank=True, max_length=255, default="")
    expires_in = models.DateTimeField(null=True)

    def __str__(self):
        return self.first_name or self.username

    def __repr__(self):
        return "{} - {}".format(self.first_name, self.username)

    def get_name(self):
        return self.first_name or self.username or self.id

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
        ordering = ["-id"]
