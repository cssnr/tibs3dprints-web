import logging

from django import template
from django.conf import settings
from django.templatetags.static import static


logger = logging.getLogger("app")
register = template.Library()


@register.simple_tag(name="get_config")
def get_config(value):
    # get django setting value or return none
    return getattr(settings, value, None)


@register.simple_tag(name="static_full")
def static_full(request, path):
    # returns the absolute_url from the absolute_uri
    return request.build_absolute_uri() + static(path).lstrip("/")


@register.filter(name="avatar_url")
def avatar_url(user):
    # return discord avatar url from user model
    if user.avatar_hash:
        return f"https://cdn.discordapp.com/avatars/" f"{user.username}/{user.avatar_hash}.png"
    else:
        return static("images/avatar.png")
