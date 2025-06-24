import io
import logging
from email.mime.image import MIMEImage
from email.utils import make_msgid

import segno
from celery import shared_task
from django.conf import settings
from django.core import management
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
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


def generate_qr_code_bytes(data: str) -> bytes:
    qr = segno.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, kind="png")
    return buffer.getvalue()


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}, rate_limit="10/m")
def send_verify_email(to_email: str, code: str, url: str, ttl=3600):
    logger.debug("send_verify_email: to_email: %s", to_email)
    try:
        # key = f"email.send.{to_email}"
        # quota = cache.get(key, 0)
        # logger.debug("quota: %s - %s", quota, key)
        # if quota >= 2:
        #     return logger.warning("Quota Exceeded for: %s", to_email)

        cid = make_msgid(domain="tibs3dprints.com")
        context = {"code": code, "url": url, "ttl": ttl, "cid": cid[1:-1]}
        logger.debug("context: %s", context)
        plain = render_to_string("email/contact.plain", context)
        html = inline_css(render_to_string("email/verify.html", context), disable_validation=True)

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

        key = f"email.send.{to_email}"
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, 600)
        else:
            cache.touch(key, 600)
    except Exception as error:
        logger.warning("send_verify_email: error: %s", error)
