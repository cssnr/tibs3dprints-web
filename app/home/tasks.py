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
from ipwhois.asn import IPASN
from ipwhois.net import Net
from premailer import transform as inline_css

from project.constants import KEY_SEND_EMAIL, KEY_SEND_IP


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
def send_verify_email(to_email: str, code: str, url: str, ip: str, ttl=3600):
    logger.debug("TASK - send_verify_email: to_email: %s", to_email)
    try:
        cid = make_msgid(domain="tibs3dprints.com")
        context = {"code": code, "url": url, "ip": ip, "ttl": ttl, "cid": cid[1:-1], "whois": lookup_ip(ip)}
        logger.debug("context: %s", context)
        plain = render_to_string("email/contact.plain", context)
        html = inline_css(render_to_string("email/verify.html", context), disable_validation=True)

        message = EmailMultiAlternatives(
            subject="Tibs3DPrints Verification Code",
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

        incr_key(KEY_SEND_EMAIL.format(to_email), 600)
        incr_key(KEY_SEND_IP.format(ip), 3600)
    except Exception as error:
        logger.warning("send_verify_email: error: %s", error)


def incr_key(key, ttl):
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, ttl)
    else:
        cache.touch(key, ttl)


def generate_qr_code_bytes(data: str) -> bytes:
    qr = segno.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, kind="png")
    return buffer.getvalue()


def lookup_ip(ip_address) -> dict:
    key = f"lookup.{ip_address}"
    if result := cache.get(key):
        logger.debug("cache.get: %s", result)
        return result
    net = Net(ip_address)
    obj = IPASN(net)
    result = obj.lookup()
    logger.debug("obj.lookup: %s", result)
    cache.set(key, result, 1210000 if result else 600)
    return result
