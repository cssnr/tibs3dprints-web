import json
import logging

import httpx
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.core import management
from django.core.cache import cache

# from django.core.cache.utils import make_template_fragment_key
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Contact, Message, MyNews


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


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 10})
def clear_news_cache():
    # Clear News cache on model update
    logger.debug("clear_news_cache")
    # return cache.delete(make_template_fragment_key('news_body'))
    return cache.delete_pattern("template.cache.news_body.*")


@shared_task()
def save_news_task(news_id, created):
    logger.debug("save_news_task - news_id: %s - created: %s", news_id, created)
    news = MyNews.objects.get(id=news_id)
    logger.debug("news: %s", news)
    if created:
        message = f"New News: {news.title}"
    else:
        message = f"News Updated: {news.title}"
    text = json.dumps({"message": message, "type": "primary"})
    channel_layer = get_channel_layer()
    event = {
        "type": "websocket.send",
        "text": text,
    }
    async_to_sync(channel_layer.group_send)("home", event)
    return "save_news_task: done"


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


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}, rate_limit="10/m")
def send_discord_message(pk):
    logger.debug("send_discord_message: pk: %s", pk)
    message = Message.objects.get(pk=pk)
    context = {"name": message.name, "message": message.message}
    discord_message = render_to_string("message/discord-message.html", context)
    logger.debug("discord_message: %s", discord_message)
    return send_discord({"content": discord_message})


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}, rate_limit="10/m")
def send_contact_email(pk):
    logger.debug("send_contact_email: pk: %s", pk)
    contact = Contact.objects.get(pk=pk)
    context = {"contact": contact, "browser": False}
    msg_html = render_to_string("email/contact.html", context)
    msg_plain = render_to_string("email/contact.plain", context)
    subject = f"Contact Form: {contact.subject}"
    count = 1
    send_mail_wrapper([settings.CONTACT_FORM_TO_EMAIL], subject, msg_plain, msg_html)
    if contact.send_copy:
        count += 1
        send_mail_wrapper([contact.email], subject, msg_plain, msg_html)
    return f"sent {count} emails"


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
