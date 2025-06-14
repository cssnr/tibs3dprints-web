import logging

import httpx
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .forms import BetaForm
from .models import BetaUser


logger = logging.getLogger("app")


def home_view(request):
    # View: /
    logger.debug("home_view: %s - %s", request.method, request.META["PATH_INFO"])
    return render(request, "home.html")


@require_http_methods(["GET", "POST"])
def beta_view(request):
    # View: /beta/
    logger.debug("beta_view: %s - %s", request.method, request.META["PATH_INFO"])
    if request.method == "GET":
        return render(request, "beta.html")

    try:
        logger.debug("request.POST: %s", request.POST)
        form = BetaForm(request.POST)
        if not form.is_valid():
            logger.debug("form.errors: %s", form.errors)
            return JsonResponse(form.errors, status=400)

        logger.debug("form.cleaned_data: %s", form.cleaned_data)

        if not request.user.is_authenticated and not google_verify(request):
            data = {"error": "Google CAPTCHA not verified."}
            return JsonResponse(data, status=400)

        data = form.cleaned_data.copy()
        existing = BetaUser.objects.filter(email=data["email"])
        if existing:
            return JsonResponse({"email": ["E-Mail Already Submitted."]}, status=400)
        beta_user = BetaUser.objects.create(**data)
        logger.debug("beta_user: %s", beta_user)
        request.session["beta_user"] = beta_user.email
        return JsonResponse({}, status=200)

    except Exception as error:
        logger.exception(error)
        return JsonResponse({"error": str(error)}, status=400)


def google_verify(request: HttpRequest) -> bool:
    if request.session.get("g_verified", False):
        return True
    try:
        url = "https://www.google.com/recaptcha/api/siteverify"
        data = {"secret": settings.GOOGLE_SITE_SECRET, "response": request.POST["g-recaptcha-response"]}
        logger.debug("data: %s", data)
        r = httpx.post(url, data=data, timeout=10)
        if r.is_success and r.json()["success"]:
            request.session["g_verified"] = True
            return True
        return False
    except Exception as error:
        logger.exception(error)
        return False
