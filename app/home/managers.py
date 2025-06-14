from django.db import models


class PollManager(models.Manager):
    def get_active(self):
        return self.filter(published=True)
