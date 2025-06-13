from django.db import models


class TikTokUser(models.Model):
    id = models.AutoField(primary_key=True)
    open_id = models.CharField(blank=True, max_length=255)
    access_token = models.CharField(blank=True, max_length=255)
    refresh_token = models.CharField(blank=True, max_length=255)
    expires_in = models.DateTimeField(null=True)

    display_name = models.CharField(blank=True, max_length=255)
    avatar_url = models.URLField(blank=True, max_length=510)

    def __str__(self):
        return self.display_name or self.open_id

    def __repr__(self):
        return f"<id={self.id} name={self.display_name} open_id={self.open_id}"

    class Meta:
        verbose_name = "TikTok User"
        verbose_name_plural = "TikTok Users"
        # ordering = ["-display_name"]
