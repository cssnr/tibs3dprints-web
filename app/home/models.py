import uuid

from django.db import models

from .managers import MyNewsManager


class TikTokUser(models.Model):
    id = models.AutoField(primary_key=True)
    open_id = models.CharField(blank=True, max_length=255)
    access_token = models.CharField(blank=True, max_length=255)
    refresh_token = models.CharField(blank=True, max_length=255)
    expires_in = models.DateTimeField(null=True)

    display_name = models.CharField(blank=True, max_length=255)
    avatar_url = models.URLField(blank=True, max_length=510)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.open_id

    def __repr__(self):
        return f"<id={self.id} name={self.display_name} open_id={self.open_id}"

    class Meta:
        verbose_name = "TikTok User"
        verbose_name_plural = "TikTok Users"
        # ordering = ["-display_name"]


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


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, verbose_name="Name")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.message[:16])

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"


class Contact(models.Model):
    email = models.EmailField(verbose_name="E-Mail Address")
    subject = models.CharField(max_length=128, verbose_name="Subject")
    message = models.TextField(
        default=False,
        verbose_name="Message",
    )
    send_copy = models.BooleanField(verbose_name="Send Copy")
    uuid = models.UUIDField(default=uuid.uuid4, verbose_name="UUID")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.email, self.subject)

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"


class MyNews(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name="Title", help_text="The Title of the post.")
    display_name = models.CharField(
        max_length=32, verbose_name="Display Name", help_text="This should be your primary alias."
    )
    description = models.TextField(
        verbose_name="Description Body", help_text="The entire body and full text of the post. Newlines are allowed."
    )
    published = models.BooleanField(
        default=True, verbose_name="Published", help_text="The post will not show up unless this is checked."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MyNewsManager()

    def __str__(self):
        return "{} - {}".format(self.display_name, self.title)

    class Meta:
        verbose_name = "My News"
        verbose_name_plural = "My News"
        ordering = ["-pk"]
