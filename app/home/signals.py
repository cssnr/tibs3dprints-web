import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from home.models import Poll


logger = logging.getLogger("app")


@receiver(post_save, sender=Poll)
@receiver(post_delete, sender=Poll)
def clear_poll_cache_signal(sender, instance, **kwargs):
    logger.debug("clear_poll_cache_signal")
    # clear_news_cache.delay()
