import io
import logging
from email.mime.image import MIMEImage
from email.utils import make_msgid

import httpx
import segno
from celery import shared_task
from django.conf import settings
from django.core import management
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from premailer import transform as inline_css


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
def send_mail_task(recipient_list, subject, message, html_message, from_email=settings.DEFAULT_FROM_EMAIL):
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


def generate_qr_code_bytes(data: str) -> bytes:
    qr = segno.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, kind="png")
    return buffer.getvalue()


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}, rate_limit="10/m")
def send_verify_email(to_email: str, code: str, url: str, ttl=3600):
    logger.debug("send_verify_email: to_email: %s", to_email)
    cid = make_msgid(domain="tibs3dprints.com")
    context = {"code": code, "url": url, "ttl": ttl, "cid": cid[1:-1]}
    logger.debug("context: %s", context)
    plain = render_to_string("email/contact.plain", context)
    html = inline_css(render_to_string("email/verify.html", context))
    message = EmailMultiAlternatives(
        subject="Tibs3DPrints E-Mail Verification",
        body=plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    message.attach_alternative(html, "text/html")
    message.mixed_subtype = "related"

    image = MIMEImage(generate_qr_code_bytes(url), name="qrcode.png")
    image.add_header("Content-Disposition", "inline", filename="qrcode.png")
    image.add_header("Content-ID", cid)
    message.attach(image)

    logger.debug("send_verify_email: message.send()")
    message.send()
