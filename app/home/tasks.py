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
    logger.debug("TASK - clear_sessions")
    return management.call_command("clearsessions")


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 2, "countdown": 10})
def flush_template_cache():
    # Flush Template Cache
    logger.debug("TASK - flush_template_cache: 'template.cache.*'")
    return cache.delete_pattern("template.cache.*")


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 2, "countdown": 10})
def clear_poll_cache():
    # Clear Poll Cache
    logger.debug("TASK - clear_poll_cache: '*.poll_view.*'")
    return cache.delete_pattern("*.poll_view.*")


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}, rate_limit="10/m")
def send_discord(message: dict, webhook=settings.DISCORD_WEBHOOK):
    logger.debug("TASK - send_discord: message: %s", message)
    logger.debug("webhook: %s", webhook)
    data = {"content": message}
    r = httpx.post(webhook, json=data, timeout=10)
    logger.debug(r.status_code)
    if not r.is_success:
        logger.warning(r.content)
        r.raise_for_status()
    return r.status_code


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}, rate_limit="10/m")
def send_mail_task(recipient_list, subject, message, html_message, from_email=settings.EMAIL_FROM_USER):
    """
    :param recipient_list: list
    :param subject: str
    :param message: str
    :param html_message: str
    :param from_email: str optional
    :return: django.core.mail.send_mail
    """
    logger.debug("TASK - send_mail_task: subject: %s", subject)
    return send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
        html_message=html_message,
    )
