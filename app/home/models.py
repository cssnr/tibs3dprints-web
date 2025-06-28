from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

from project.helpers import gen_auth

from .managers import PollManager


class AppUser(AbstractBaseUser):
    # User Fields
    email = models.EmailField(blank=True, unique=True)
    name = models.CharField(blank=True, max_length=255)
    verified = models.BooleanField(default=False)
    authorization = models.CharField(default=gen_auth, max_length=255)
    password = models.CharField(blank=True, max_length=255, editable=False)
    points = models.IntegerField(default=0)

    # # TikTok Fields
    # display_name = models.CharField(blank=True, max_length=255)
    # avatar_url = models.URLField(blank=True, max_length=510)
    # open_id = models.CharField(blank=True, max_length=255, editable=False)
    # access_token = models.CharField(blank=True, max_length=255, editable=False)
    # refresh_token = models.CharField(blank=True, max_length=255, editable=False)
    # expires_in = models.DateTimeField(null=True, editable=False)

    # Meta Fields
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.email

    def __repr__(self):
        return f"<id={self.id} name={self.name} email={self.email}"

    class Meta:
        verbose_name = "App User"
        verbose_name_plural = "App Users"
        ordering = ["-id"]


class BetaUser(models.Model):
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
    title = models.CharField(max_length=255, verbose_name="Title")
    question = models.CharField(max_length=255, verbose_name="Question")
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

    def is_active(self) -> bool:
        return self.start_at <= now() <= self.end_at

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
    file = models.FileField(upload_to="choice/%Y/%m/", verbose_name="Image")
    votes = models.IntegerField(default=0, verbose_name="Votes")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        verbose_name = "Choice"
        verbose_name_plural = "Choices"
        ordering = ["-id"]


class Vote(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
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


class Point(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.user.email, self.points)

    def __repr__(self):
        return "{} - {} - {}".format(self.user.email, self.points, self.reason[:32])

    class Meta:
        verbose_name = "Point"
        verbose_name_plural = "Points"
        ordering = ["-id"]
