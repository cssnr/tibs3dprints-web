import logging

import httpx
from celery import shared_task
from django.conf import settings
from django.core import management
from django.core.cache import cache
from django.core.mail import send_mail


logger = logging.getLogger("app")


@shared_task()
def clear_sessions():
    # Cleanup session data for supported backends
    logger.debug("clear_sessions")
    return management.call_command("clearsessions")


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 2, "countdown": 10})
def flush_template_cache():
    # Flush template cache on request
    logger.debug("flush_template_cache")
    return cache.delete_pattern("template.cache.*")


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}, rate_limit="10/m")
def send_discord(message: dict, webhook=settings.DISCORD_WEBHOOK):
    logger.debug("send_discord: message: %s", message)
    logger.debug("webhook: %s", webhook)
    data = {"content": message}
    r = httpx.post(webhook, json=data, timeout=10)
    logger.debug(r.status_code)
    if not r.is_success:
        logger.warning(r.content)
        r.raise_for_status()
    return r.status_code


def send_mail_wrapper(recipient_list, subject, message, html_message):
    """
    :param recipient_list: list
    :param subject: str
    :param message: str
    :param html_message: str
    :return: django.core.mail.send_mail
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_FROM_USER,
        recipient_list=recipient_list,
        fail_silently=False,
        html_message=html_message,
    )
