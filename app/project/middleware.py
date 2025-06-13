import zoneinfo

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            time_zone = request.COOKIES.get("timezone")
            if time_zone:
                timezone.activate(zoneinfo.ZoneInfo(time_zone))
            else:
                timezone.deactivate()
        except Exception:
            timezone.deactivate()

        return self.get_response(request)
