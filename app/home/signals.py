import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from home.models import Choice, Poll
from home.tasks import clear_poll_cache


logger = logging.getLogger("app")


@receiver(post_delete, sender=Choice)
def choice_post_delete_file_delete(sender, instance, **kwargs):
    logger.debug("SIGNAL - choice_post_delete_file_delete")
    if instance.file:
        instance.file.delete(save=False)


@receiver(post_save, sender=Poll)
@receiver(post_delete, sender=Poll)
def poll_post_clear_cache(sender, instance, **kwargs):
    logger.debug("SIGNAL - clear_poll_cache")
    clear_poll_cache.delay()
