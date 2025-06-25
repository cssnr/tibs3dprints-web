import logging

import httpx
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from .forms import BetaForm
from .models import BetaUser


logger = logging.getLogger("app")


def home_view(request):
    """
    View  /
    """
    logger.debug("home_view: %s - %s", request.method, request.META["PATH_INFO"])
    return render(request, "home.html")


def app_view(request):
    """
    View  /app/
    """
    logger.debug("app_view: %s - %s", request.method, request.META["PATH_INFO"])
    return render(request, "app.html")


def beta_view(request):
    """
    View  /beta/
    """
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


# def verify_view(request, base64_str):
#     """
#     View  /verify/:base64_str/
#     """
#     logger.debug("verify_view: %s - %s", request.method, request.META["PATH_INFO"])
#     logger.debug("-" * 20)
#     context = {"verified": False, "message": "Unknown"}
#     try:
#         logger.debug("base64_str: %s", base64_str)
#         decoded_string = base64.urlsafe_b64decode(base64_str.encode("utf-8")).decode("utf-8")
#         logger.debug("decoded_string: %s", decoded_string)
#         data = json.loads(decoded_string)
#         logger.debug("data: %s", data)
#         context["email"] = data["email"]
#
#         verified, message = verify_email_code(data["email"], data["code"])
#         logger.debug("verified: %s - %s", verified, message)
#         context["verified"] = verified
#         context["message"] = message
#
#     except Exception as error:
#         logger.exception(error)
#
#     logger.debug("context: %s", context)
#     return render(request, "verify.html", context)
