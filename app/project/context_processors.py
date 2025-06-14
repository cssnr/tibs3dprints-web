# import zoneinfo
# from django.utils import timezone
# from django.core.cache import cache
# from django.forms.models import model_to_dict


def site(request):
    # try:
    #     time_zone = request.COOKIES.get("timezone")
    #     if time_zone:
    #         timezone.activate(zoneinfo.ZoneInfo(time_zone))
    #     else:
    #         timezone.deactivate()
    # except Exception:
    #     timezone.deactivate()

    meta = {
        "author": "Shane",
        "title": "Tibs3DPrints Web",
        "description": "Tibs3DPrints Web App. Coming Soon...",
    }

    navigation = [
        {"name": "Home", "url": "home:index", "path": "/"},
    ]

    return {
        "meta": meta,
        "navigation": navigation,
    }
