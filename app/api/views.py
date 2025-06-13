import json
import logging
from datetime import datetime, timedelta

import httpx
from decouple import config
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from api.models import TikTokUser
from home.tasks import send_discord


logger = logging.getLogger("app")
log = logging.getLogger("app")
cache_seconds = 60 * 60 * 4


@csrf_exempt
def api_view(request):
    """
    View  /api/
    """
    log.debug("api_view: %s - %s", request.method, request.META["PATH_INFO"])
    log.debug("-" * 20)

    try:
        log.debug("-" * 20 + "\n" + json.dumps(request.META) + "\n")
    except:  # noqa: E722
        log.debug("*" * 20)
        log.debug(request.META)
    log.debug("-" * 20)

    try:
        log.debug("-" * 20 + "\n" + request.body.decode("utf-8") + "\n")
    except:  # noqa: E722
        log.debug("*" * 20)
        log.debug(request.body)
    log.debug("-" * 20)

    try:
        log.debug(json.loads(request.body.decode("utf-8")))
    except:  # noqa: E722
        log.debug("Unable to json.loads - request.body.decode()")
    log.debug("-" * 20)

    try:
        data = json.loads(request.body.decode("utf-8"))
        content = {"content": f"```json\n{data}\n```"}
        send_discord(content, settings.DISCORD_WEBHOOK)
    except Exception as error:
        log.error(error)

    # messages.info(request, 'Welcome Home.')
    return HttpResponse()


@require_http_methods(["POST"])
@csrf_exempt
def auth_view(request):
    """
    View  /api/auth/
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        log.debug("data: %s", data)
        code = data["code"]
        code_verifier = data["codeVerifier"]
        response = get_access_token(code, code_verifier)
        log.debug("response: %s", response)
        access_token = response.get("access_token")
        log.debug("access_token: %s", access_token)
        if access_token:
            profile = get_user_profile(access_token)
            log.debug("profile: %s", profile)
            user = profile.get("data", {}).get("user", {})
            log.debug("user: %s", user)

            tiktoker, created = TikTokUser.objects.get_or_create(
                open_id=response["open_id"],
            )
            log.debug("tiktoker: %s", tiktoker)
            log.debug("created: %s", created)

            tiktoker.access_token = access_token
            tiktoker.open_id = response["open_id"]
            tiktoker.refresh_token = response["refresh_token"]
            tiktoker.expires_in = datetime.now() + timedelta(0, response["expires_in"])
            tiktoker.display_name = user.get("display_name", "")
            tiktoker.avatar_url = user.get("avatar_url", "")

            tiktoker.save()
            return JsonResponse(user)
        else:
            error_description = response.get("error_description", "Unknown")
            return JsonResponse({"error": error_description}, status=401)
    except Exception as error:
        log.error(error)
        return JsonResponse({"error": str(error)}, status=500)


def get_access_token(code: str, code_verifier: str) -> dict:
    """
    Post OAuth code and Return access_token
    """
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    data = {
        "client_key": config("TIKTOK_CLIENT_KEY"),
        "client_secret": config("TIKTOK_CLIENT_SECRET"),
        "redirect_uri": config("TIKTOK_REDIRECT_URI"),
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
        "code": code,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = httpx.post(url, data=data, headers=headers, timeout=10)
    log.debug("r: %s", r)
    if not r.is_success:
        logger.info("status_code: %s", r.status_code)
        r.raise_for_status()
    return r.json()


def get_user_profile(access_token: str) -> dict:
    """
    Get Profile for Authenticated User
    """
    url = "https://open.tiktokapis.com/v2/user/info/"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"fields": "open_id,union_id,avatar_url,display_name"}
    r = httpx.get(url, headers=headers, params=params, timeout=10)
    logger.info("r: %s", r)
    if not r.is_success:
        logger.info("status_code: %s", r.status_code)
        r.raise_for_status()
    return r.json()
