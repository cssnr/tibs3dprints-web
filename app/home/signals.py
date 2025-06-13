import logging

# from celery.signals import worker_ready
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from home.models import MyNews
from home.tasks import clear_news_cache, save_news_task


# from django.forms.models import model_to_dict


logger = logging.getLogger("app")


# @worker_ready.connect
# def run_startup_task(sender, **kwargs):
#     app_startup.delay()


@receiver(post_save, sender=MyNews)
@receiver(post_delete, sender=MyNews)
def clear_news_cache_signal(sender, instance, **kwargs):
    logger.debug("clear_news_cache_signal")
    # clear_news_cache.delay()


@receiver(post_save, sender=MyNews)
def save_news_signal(sender, instance, **kwargs):
    logger.debug("save_news_signal: %s, %s, %s", sender, instance, kwargs)
    save_news_task(instance.id, kwargs.get("created", False))
