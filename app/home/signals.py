import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from home.models import Choice, Poll, Vote
from home.tasks import clear_poll_cache


logger = logging.getLogger("app")


@receiver(post_delete, sender=Choice)
def choice_post_delete_file_delete(sender, instance, **kwargs):
    logger.debug("SIGNAL - choice_post_delete_file_delete")
    if instance.file:
        instance.file.delete(save=False)


@receiver(post_save, sender=Poll)
@receiver(post_delete, sender=Poll)
def poll_clear_cache_signal(sender, instance, **kwargs):
    logger.debug("SIGNAL - poll_clear_cache_signal")
    clear_poll_cache.delay()


@receiver(post_save, sender=Vote)
@receiver(post_delete, sender=Vote)
def vote_clear_cache_signal(sender, instance, **kwargs):
    logger.debug("SIGNAL - vote_clear_cache_signal")
    clear_poll_cache.delay()
