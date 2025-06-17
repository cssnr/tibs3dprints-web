from django.db import models
from django.utils.timezone import now


class PollManager(models.Manager):
    def get_active(self):
        return (
            self.prefetch_related("choice_set")
            .filter(start_at__lte=now(), end_at__gt=now())
            .order_by("start_at")
            .first()
        )
