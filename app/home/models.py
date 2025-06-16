from django.core.exceptions import ValidationError
from django.db import models

from project.helpers import gen_auth

from .managers import PollManager


class TikTokUser(models.Model):
    id = models.AutoField(primary_key=True)
    authorization = models.CharField(default=gen_auth, max_length=255)

    first_name = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(blank=True, max_length=255)
    email_address = models.EmailField(blank=True)

    open_id = models.CharField(blank=True, max_length=255)
    access_token = models.CharField(blank=True, max_length=255)
    refresh_token = models.CharField(blank=True, max_length=255)
    expires_in = models.DateTimeField(null=True)

    display_name = models.CharField(blank=True, max_length=255)
    avatar_url = models.URLField(blank=True, max_length=510)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.open_id or "New User"

    def __repr__(self):
        return f"<id={self.id} name={self.display_name} open_id={self.open_id}"

    class Meta:
        verbose_name = "TikTok User"
        verbose_name_plural = "TikTok Users"
        ordering = ["-id"]


class BetaUser(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name="E-Mail", unique=True)
    name = models.CharField(max_length=255, verbose_name="Name")
    details = models.TextField(verbose_name="Details", blank=True)
    added = models.BooleanField(verbose_name="Added", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.name[:16], self.email[:16])

    class Meta:
        verbose_name = "Beta User"
        verbose_name_plural = "Beta Users"
        ordering = ["-id"]


class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="Title")
    question = models.TextField(verbose_name="Question")
    start_at = models.DateTimeField(verbose_name="Start Date")
    end_at = models.DateTimeField(verbose_name="End Date")
    objects = PollManager()

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        verbose_name = "Poll"
        verbose_name_plural = "Polls"
        ordering = ["-id"]

    def clean(self):
        overlapping = Poll.objects.filter(
            end_at__gt=self.start_at,
            start_at__lt=self.end_at,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("Poll time overlaps with an existing poll.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name="Name")
    file = models.FileField(upload_to=".", verbose_name="Image")
    votes = models.IntegerField(default=0, verbose_name="Votes")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        verbose_name = "Choice"
        verbose_name_plural = "Choices"
        ordering = ["-id"]


class Vote(models.Model):
    user = models.ForeignKey(TikTokUser, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    notify_on_result = models.BooleanField(default=False)
    voted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.poll.title[:16], self.choice.name[:16])

    def __repr__(self):
        return "{} - {}".format(self.poll.title[:16], self.choice.name[:16])

    class Meta:
        unique_together = ("user", "poll")
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        ordering = ["-id"]
