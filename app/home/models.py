import uuid

from django.db import models

from .managers import MyNewsManager


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
