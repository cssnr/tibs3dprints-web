from django.db import models


class MyNewsManager(models.Manager):
    def get_active(self):
        return self.filter(published=True)
