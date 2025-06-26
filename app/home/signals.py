import logging

from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from home.models import Choice, Point, Poll, Vote
from home.tasks import clear_poll_cache


logger = logging.getLogger("app")


@receiver(post_delete, sender=Choice)
def choice_post_delete_file_delete(sender, instance, **kwargs):
    logger.debug("SIGNAL - choice_post_delete_file_delete")
    if instance.file:
        logger.debug("instance.file.delete: %s", instance.file)
        instance.file.delete(save=False)


@receiver(post_save, sender=Poll)
@receiver(post_delete, sender=Poll)
def poll_clear_cache_signal(**kwargs):
    logger.debug("SIGNAL - poll_clear_cache_signal")
    clear_poll_cache.delay()


@receiver(post_save, sender=Vote)
@receiver(post_delete, sender=Vote)
def vote_clear_cache_signal(**kwargs):
    logger.debug("SIGNAL - vote_clear_cache_signal")
    clear_poll_cache.delay()


@receiver(post_save, sender=Point)
def update_user_points_signal(sender, instance, created, **kwargs):
    logger.debug("SIGNAL - update_user_points_signal: created: %s", created)
    logger.debug("instance: %s", instance)
    logger.debug("instance.user: %s", instance.user)
    if created:
        instance.user.points += instance.points
        instance.user.save(update_fields=["points"])


@receiver(post_save, sender=Vote)
def vote_choice_increment_signal(sender, instance, created, **kwargs):
    logger.debug("SIGNAL - vote_choice_increment_signal: created: %s", created)
    logger.debug("instance: %s", instance)
    logger.debug("instance.choice: %s", instance.choice)
    if created:
        instance.choice.votes = F("votes") + 1
        instance.choice.save(update_fields=["votes"])
