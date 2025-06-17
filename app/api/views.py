import json
import logging
from datetime import datetime, timedelta
from functools import wraps

import httpx
from decouple import config
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from home.models import Choice, Poll, TikTokUser, Vote
from home.tasks import send_discord


logger = logging.getLogger("app")
# cache_seconds = 60 * 60 * 4


def tiktok_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        authorization = request.headers.get("Authorization")
        logger.debug("authorization: %s", authorization)
        if not authorization:
            logger.warning("Missing Authorization header")
            return JsonResponse({"error": "Authorization required"}, status=401)

        try:
            user = TikTokUser.objects.get(authorization=authorization)
            request.user = user
        except TikTokUser.DoesNotExist:
            logger.warning("Invalid Authorization token: %s", authorization)
            return JsonResponse({"error": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view


@csrf_exempt
def api_view(request):
    """
    View  /api/
    """
    logger.debug("api_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("-" * 20)

    try:
        logger.debug("-" * 20 + "\n" + json.dumps(request.META) + "\n")
    except:  # noqa: E722
        logger.debug("*" * 20)
        logger.debug(request.META)
    logger.debug("-" * 20)

    try:
        logger.debug("-" * 20 + "\n" + request.body.decode("utf-8") + "\n")
    except:  # noqa: E722
        logger.debug("*" * 20)
        logger.debug(request.body)
    logger.debug("-" * 20)

    try:
        logger.debug(json.loads(request.body.decode("utf-8")))
    except:  # noqa: E722
        logger.debug("Unable to json.loads - request.body.decode()")
    logger.debug("-" * 20)

    try:
        data = json.loads(request.body.decode("utf-8"))
        content = {"content": f"```json\n{data}\n```"}
        send_discord(content, settings.DISCORD_WEBHOOK)
    except Exception as error:
        logger.error(error)

    return HttpResponse("Online.")


@require_http_methods(["POST"])
@csrf_exempt
def auth_view(request):
    """
    View  /api/auth/
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.debug("data: %s", data)
        code = data["code"]
        code_verifier = data["codeVerifier"]
        if not code or not code_verifier:
            return JsonResponse({"error": "Invalid Request."}, status=400)
        response = get_access_token(code, code_verifier)
        logger.debug("response: %s", response)
        access_token = response.get("access_token")
        logger.debug("access_token: %s", access_token)
        if access_token:
            profile = get_user_profile(access_token)
            logger.debug("profile: %s", profile)
            user = profile.get("data", {}).get("user", {})
            logger.debug("user: %s", user)

            tiktoker, created = TikTokUser.objects.get_or_create(
                open_id=response["open_id"],
            )
            logger.debug("tiktoker: %s", tiktoker)
            logger.debug("created: %s", created)

            tiktoker.access_token = access_token
            tiktoker.open_id = response["open_id"]
            tiktoker.refresh_token = response["refresh_token"]
            tiktoker.expires_in = datetime.now() + timedelta(0, response["expires_in"])
            tiktoker.display_name = user.get("display_name", "")
            tiktoker.avatar_url = user.get("avatar_url", "")

            tiktoker.save()
            logger.debug("tiktoker: %s", tiktoker)
            logger.debug("authorization: %s", tiktoker.authorization)
            user["authorization"] = tiktoker.authorization
            logger.debug("user: %s", user)
            return JsonResponse(user)
        else:
            error_description = response.get("error_description", "Unknown")
            return JsonResponse({"error": error_description}, status=401)
    except Exception as error:
        logger.error(error)
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
    logger.debug("r: %s", r)
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


@csrf_exempt
@tiktok_auth_required
def poll_current_view(request):
    """
    View  /api/poll/current/
    """
    logger.debug("poll_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("-" * 20)
    poll = Poll.objects.get_active()
    logger.debug("poll: %s", poll)
    if not poll:
        return JsonResponse(None, safe=False)
    data = {
        "poll": model_to_dict(poll),
        "choices": [serialize_choice(choice) for choice in poll.choice_set.all()],
        "vote": serialize_vote(Vote.objects.filter(user=request.user, poll=poll).first()),
    }
    return JsonResponse(data)


@csrf_exempt
@tiktok_auth_required
@require_http_methods(["POST"])
def poll_vote_view(request):
    """
    View  /api/poll/vote/
    """
    logger.debug("poll_vote_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("-" * 20)
    logger.debug("user: %s", request.user)
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.debug("data: %s", data)
        poll = Poll.objects.get(id=data["poll"])
        logger.debug("poll: %s", poll)
        if not poll.is_active():
            return JsonResponse({"error": "Poll Not Active"}, status=400)
        choice = Choice.objects.get(id=data["choice"])
        logger.debug("choice: %s", choice)
        try:
            vote = Vote.objects.create(user=request.user, poll=poll, choice=choice)
            logger.debug("vote: %s", vote)
            with transaction.atomic():
                choice.votes = F("votes") + 1
                choice.save(update_fields=["votes"])
                choice.refresh_from_db()
        except IntegrityError as error:
            logger.debug("error: %s", error)
            return JsonResponse({"error": "Already Voted"}, status=400)

        return JsonResponse(serialize_vote(vote), status=200)

    except Exception as error:
        logger.error(error)
        return JsonResponse({"error": str(error)}, status=500)


def serialize_choice(choice):
    data = model_to_dict(choice)
    data["file"] = choice.file.url if choice.file else None
    return data


def serialize_vote(vote):
    if vote is None:
        return None
    return {
        "id": vote.id,
        "user_id": vote.user_id,
        "poll_id": vote.poll_id,
        "choice_id": vote.choice_id,
        "notify_on_result": vote.notify_on_result,
        "voted_at": vote.voted_at.isoformat() if vote.voted_at else None,
    }
