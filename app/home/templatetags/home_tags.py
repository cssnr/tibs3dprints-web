import logging

from decouple import config
from django import template
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse


logger = logging.getLogger("app")
register = template.Library()


@register.simple_tag(name="get_config")
def get_config(value):
    # get django setting value, config value, or empty string
    return getattr(settings, value, config(value, default=""))


@register.simple_tag(name="static_full")
def static_full(request, path):
    # returns the absolute_url from the absolute_uri
    return request.build_absolute_uri() + static(path).lstrip("/")


@register.simple_tag(name="url_full")
def url_full(path):
    # returns the full_url for the reversed path
    logger.debug("url_full: path: %s", path)
    return settings.SITE_URL + reverse(path)


@register.simple_tag(name="url_full_kwarg")
def url_full_kwarg(path, key, arg):
    # returns the full_url for the reversed path with a kwarg
    logger.debug("path: %s - key: %s - arg: %s", path, key, arg)
    return settings.SITE_URL + reverse(path, kwargs={key: arg})


@register.simple_tag(name="country_emoji")
def country_emoji(country_code):
    # returns the full_url for the reversed path with a kwarg
    logger.debug("country_emoji: country_code: %s", country_code)
    try:
        return "".join(chr(ord(c) + 127397) for c in country_code.upper())
    except Exception:
        return country_code


@register.simple_tag(name="sec_to_human")
def sec_to_human(seconds):
    # returns seconds to human-readable time
    logger.debug("sec_to_human: seconds: %s", seconds)
    try:
        seconds = int(seconds)
    except Exception:
        return "Unknown"

    def fmt_int(value: int, string: str):
        s = "" if value == 1 else "s"
        return f"{value} {string}{s}"

    m, _ = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        if m:
            return f"{fmt_int(h, 'hour')} {fmt_int(m, 'minute')}"
        else:
            return fmt_int(h, "hour")
    else:
        return fmt_int(m, "minute")


@register.filter(name="avatar_url")
def avatar_url(user):
    # return discord avatar url from user model
    if user.avatar_hash:
        return f"https://cdn.discordapp.com/avatars/{user.username}/{user.avatar_hash}.png"
    else:
        return static("images/avatar.png")
