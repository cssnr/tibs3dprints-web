import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from secrets import randbelow
from typing import Union
from urllib import parse

import httpx
from decouple import config
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from home.models import AppUser, Choice, Point, Poll, Vote
from home.tasks import send_verify_email
from project.constants import KEY_AUTH_CODE, KEY_AUTH_SEND, KEY_AUTH_STATE


logger = logging.getLogger("app")
auth_code_ttl = 3600

# signer = TimestampSigner()


def auth_from_token(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        authorization = request.headers.get("Authorization")
        logger.debug("authorization: %s", authorization)
        if not authorization:
            logger.warning("Missing Authorization header")
            return JsonResponse({"message": "Authorization required"}, status=401)

        try:
            user = AppUser.objects.get(authorization=authorization)
            request.user = user
        except AppUser.DoesNotExist:
            logger.warning("Invalid Authorization token: %s", authorization)
            return JsonResponse({"message": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view


@csrf_exempt
def api_view(request):
    """
    View  /api/
    """
    logger.debug("api_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("-" * 20)
    return HttpResponse("Online.")


@csrf_exempt
@require_http_methods(["POST"])
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
            return JsonResponse({"message": "Invalid Request."}, status=400)
        response = get_access_token(code, code_verifier)
        logger.debug("response: %s", response)
        access_token = response.get("access_token")
        logger.debug("access_token: %s", access_token)
        if access_token:
            profile = get_user_profile(access_token)
            logger.debug("profile: %s", profile)
            user_data = profile.get("data", {}).get("user", {})
            logger.debug("user_data: %s", user_data)

            user, created = AppUser.objects.get_or_create(open_id=response["open_id"])
            logger.debug("user: %s", user)
            logger.debug("created: %s", created)

            user.access_token = access_token
            user.open_id = response["open_id"]
            user.refresh_token = response["refresh_token"]
            user.expires_in = datetime.now() + timedelta(0, response["expires_in"])
            user.display_name = user_data.get("display_name", "")
            user.avatar_url = user_data.get("avatar_url", "")

            user.save()
            logger.debug("user: %s", user)
            logger.debug("authorization: %s", user.authorization)
            user_data["authorization"] = user.authorization
            logger.debug("user_data: %s", user_data)
            return JsonResponse(user_data)
        else:
            error_description = response.get("error_description", "Unknown")
            return JsonResponse({"message": error_description}, status=401)
    except Exception as error:
        logger.error(error)
        return JsonResponse({"message": str(error)}, status=500)


def get_access_token(code: str, code_verifier: str) -> dict:
    # Post OAuth code and Return access_token
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
    # Get Profile for Authenticated User
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
@auth_from_token
@cache_page(60 * 5, key_prefix="poll_view")
def poll_current_view(request):
    """
    View  /api/poll/current/
    """
    logger.debug("poll_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("auth_from_token: %s", request.user)
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
@auth_from_token
@require_http_methods(["POST"])
def poll_vote_view(request):
    """
    View  /api/poll/vote/
    """
    logger.debug("poll_vote_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("auth_from_token: %s", request.user)
    logger.debug("-" * 20)
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.debug("data: %s", data)
        poll = Poll.objects.get(id=data["poll"])
        logger.debug("poll: %s", poll)
        if not poll.is_active():
            return JsonResponse({"message": "Poll Not Active"}, status=400)
        choice = Choice.objects.get(id=data["choice"])
        logger.debug("choice: %s", choice)
        try:
            with transaction.atomic():
                vote = Vote.objects.create(user=request.user, poll=poll, choice=choice)
                logger.debug("vote: %s", vote)
                point = Point.objects.create(user=request.user, points=10, reason=f"Voted on Poll {poll.title}")
                logger.debug("point: %s", point)

        except IntegrityError as error:
            logger.debug("error: %s", error)
            return JsonResponse({"message": "Already Voted"}, status=400)

        return JsonResponse(serialize_vote(vote), status=200)

    except Exception as error:
        logger.error(error)
        return JsonResponse({"message": str(error)}, status=500)


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


# @csrf_exempt
# @require_http_methods(["POST"])
# def auth_register_view(request):
#     """
#     View  /api/auth/register/
#     """
#     logger.debug("auth_register_view: %s - %s", request.method, request.META["PATH_INFO"])
#     logger.debug("-" * 20)
#     try:
#         data = json.loads(request.body.decode("utf-8"))
#         logger.debug("data: %s", data)
#
#         # ChatGPT is Retarded Section
#         temp_user = AppUser(email=data["email"], name=data.get("name"))
#         validate_password(data["password"], user=temp_user)
#
#         # ChatGPT is EXTRA RETARDED Section
#         user = AppUser.objects.create(email=data["email"], name=data.get("name"))
#         user.set_password(data["password"])
#         user.save()
#
#         send_verify_email(request, user.email)
#         logger.debug("user: %s", user)
#         return JsonResponse(model_to_dict(user), status=200)
#     except Exception as error:
#         logger.error(error)
#         return JsonResponse({"message": str(error)}, status=500)


# @csrf_exempt
# @require_http_methods(["POST"])
# def email_check_view(request):
#     """
#     View  /api/email/check/
#     """
#     logger.debug("email_edit_check: %s - %s", request.method, request.META["PATH_INFO"])
#     logger.debug("-" * 20)
#     try:
#         data = json.loads(request.body.decode("utf-8"))
#         logger.debug("data: %s", data)
#         q = AppUser.objects.filter(email=data["email"])
#         if not q:
#             return JsonResponse({"message": "Available"}, status=200)
#         return JsonResponse({"message": "Unavailable"}, status=400)
#
#     except Exception as error:
#         logger.error(error)
#         return JsonResponse({"message": str(error)}, status=500)


@csrf_exempt
@auth_from_token
def user_current_view(request):
    """
    View  /api/user/current/
    """
    logger.debug("user_current_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("auth_from_token: %s", request.user)
    logger.debug("-" * 20)
    try:
        return JsonResponse(serialize_user(request.user), status=200)
    except Exception as error:
        logger.error(error)
        return JsonResponse({"message": str(error)}, status=401)


@csrf_exempt
@auth_from_token
def user_edit_view(request):
    """
    View  /api/user/edit/
    """
    logger.debug("user_edit_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("auth_from_token: %s", request.user)
    logger.debug("-" * 20)
    user_editables = ["name"]
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.debug("data: %s", data)
        update_fields = []
        for key, value in data.items():
            if key in user_editables and value is not None:
                logger.debug("setattr: %s - %s", key, value)
                setattr(request.user, key, value)
                update_fields.append(key)
        # if not update_fields:
        #     return JsonResponse({"message": "Not Changed"}, status=304)
        request.user.save(update_fields=update_fields)
        return JsonResponse(serialize_user(request.user), status=200)
    except Exception as error:
        logger.error(error)
        return JsonResponse({"message": str(error)}, status=500)


def serialize_user(user: Union[AppUser, AnonymousUser]):
    return model_to_dict(user, exclude=["id", "last_login"])


# @csrf_exempt
# @auth_from_token
# @require_http_methods(["POST"])
# def email_edit_view(request):
#     """
#     View  /api/email/edit/
#     """
#     logger.debug("email_edit_view: %s - %s", request.method, request.META["PATH_INFO"])
#     logger.debug("auth_from_token: %s", request.user)
#     logger.debug("-" * 20)
#     try:
#         data = json.loads(request.body.decode("utf-8"))
#         logger.debug("data: %s", data)
#         try:
#             validate_email(data["email"])
#         except ValidationError as e:
#             print("bad email, details:", e)
#             return JsonResponse({"message": "Invaild E-Mail Address"}, status=400)
#
#         if request.user.email == data["email"]:
#             return JsonResponse({"message": "E-Mail Not Changed"}, status=400)
#
#         request.user.email = data["email"]
#         request.user.verified = False
#         request.user.save()
#
#         send_verify_email(request, data["email"])
#
#         return JsonResponse({"message": "Success"}, status=200)
#
#     except Exception as error:
#         logger.error(error)
#         return JsonResponse({"message": str(error)}, status=500)


# @csrf_exempt
# @auth_from_token
# @require_http_methods(["POST"])
# def email_verify_view(request):
#     """
#     View  /api/email/verify/
#     """
#     logger.debug("email_verify_view: %s - %s", request.method, request.META["PATH_INFO"])
#     logger.debug("auth_from_token: %s", request.user)
#     logger.debug("-" * 20)
#     try:
#         data = json.loads(request.body.decode("utf-8"))
#         logger.debug("data: %s", data)
#
#         verified, message = verify_email_code(data["email"], data["code"])
#         logger.debug("verified: %s - %s", verified, message)
#
#         return JsonResponse({"verified": verified, "message": message}, status=200)
#
#     except Exception as error:
#         logger.error(error)
#         return JsonResponse({"message": str(error)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def auth_login_view(request):
    """
    View  /api/auth/login/
    POST: email, code, state -> send auth
    """
    logger.debug("auth_login_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("-" * 20)
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.debug("data: %s", data)
        logger.debug("data.email: %s", data["email"])
        logger.debug("data.code: %s", data["code"])
        logger.debug("data.state: %s", data["state"])
        logger.debug("-" * 20)
        email = data["email"]
        code = cache.get(KEY_AUTH_CODE.format(email))
        state = cache.get(KEY_AUTH_STATE.format(email))
        logger.debug("code: %s", code)
        logger.debug("state: %s", state)

        if str(code) != str(data["code"]):
            logger.debug('code: "%s" != "%s"', code, data["code"])
            return JsonResponse({"message": "Invalid Code"}, status=401)
        if str(state) != str(data["state"]):
            logger.debug('state: "%s" != "%s"', state, data["state"])
            return JsonResponse({"message": "Invalid State"}, status=401)

        # user = get_object_or_404(AppUser, email=data["email"])
        user, created = AppUser.objects.get_or_create(email=email)
        logger.debug("user: %s", user)
        logger.debug("created: %s", created)
        if not user:
            return JsonResponse({"message": "Error Creating User"}, status=401)

        fields_to_update = ["last_login"]
        if not user.verified:
            user.verified = True
            fields_to_update.append("verified")
        logger.debug("fields_to_update: %s", fields_to_update)
        user.last_login = now()
        user.save(update_fields=fields_to_update)
        result = cache.delete_many([KEY_AUTH_CODE.format(email), KEY_AUTH_STATE.format(email)])
        logger.debug("cache.delete_many: %s", result)
        return JsonResponse(serialize_user(user), status=200)
    except Exception as error:
        logger.error(error)
        return JsonResponse({"message": str(error)}, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def auth_start_view(request):
    """
    View  /api/auth/start/
    POST: email, state -> send code email
    """
    logger.debug("auth_start_view: %s - %s", request.method, request.META["PATH_INFO"])
    logger.debug("-" * 20)
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.debug("data: %s", data)
        state = data["state"]
        logger.debug("state: %s", state)
        email = data["email"]
        logger.debug("email: %s", email)

        if len(state) < 24:
            return JsonResponse({"message": "Invalid State"}, status=400)
        try:
            validate_email(email)
        except ValidationError as e:
            logger.debug("ValidationError: %s", e)
            return JsonResponse({"message": "E-Mail Address Invalid"}, status=400)

        # user, created = AppUser.objects.get_or_create(email=data["email"])
        # logger.debug("user: %s", user)
        # logger.debug("created: %s", created)
        # logger.debug("verified: %s", user.verified)

        quota = cache.get_or_set(KEY_AUTH_SEND.format(email), 0, 600)
        logger.debug("quota: %s", quota)
        if quota >= 2:
            logger.warning("Quota Exceeded for: %s", email)
            return JsonResponse({"message": "Quota Exceeded."}, status=400)

        code = str(randbelow(9000) + 1000)
        logger.debug("code: %s", code)
        cache.set(KEY_AUTH_CODE.format(email), code, auth_code_ttl)
        cache.set(KEY_AUTH_STATE.format(email), data["state"], auth_code_ttl)

        # signature = get_signature(user_id=user.id, code=code)
        # logger.debug("signature: %s", signature)
        url = get_signed_url(code=code)
        logger.debug("url: %s", url)

        send_verify_email.delay(email, code, url)
        return JsonResponse({"message": "E-Mail Queued"}, status=200)
    except Exception as error:
        logger.error(error)
        return JsonResponse({"message": str(error)}, status=500)


def get_signed_url(**kwargs) -> str:
    logger.debug("get_signed_url: %s", kwargs)
    encoded = parse.urlencode(kwargs)
    logger.debug("encoded: %s", encoded)
    url = f"{settings.DEEP_URL}/auth/local?{encoded}"
    return url


# def generate_qr_code_bytes(data: str) -> bytes:
#     qr = segno.make(data)
#     buffer = io.BytesIO()
#     qr.save(buffer, kind="png")
#     return buffer.getvalue()
#
#
# def send_verify_email(user, code, url, ttl=auth_code_ttl):
#     qr_image_bytes = generate_qr_code_bytes(url)
#     cid = make_msgid(domain="tibs3dprints.com")
#     logger.debug("cid: %s", cid)
#     context = {"code": code, "url": url, "ttl": ttl, "cid": cid[1:-1]}
#     logger.debug("context: %s", context)
#
#     subject = "Tibs3DPrints E-Mail Verification"
#     plain = render_to_string("email/contact.plain", context)
#     html = inline_css(render_to_string("email/verify.html", context))
#
#     msg = EmailMultiAlternatives(
#         subject=subject,
#         body=plain,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[user.email],
#     )
#     msg.attach_alternative(html, "text/html")
#
#     msg.mixed_subtype = "related"
#
#     img = MIMEImage(qr_image_bytes, name="qrcode.png")
#     img.add_header("Content-ID", cid)
#     img.add_header("Content-Disposition", "inline", filename="qrcode.png")
#     msg.attach(img)
#
#     logger.debug("START")
#     msg.send()
#     logger.debug("DONE")


# def get_signature(**kwargs):
#     value = json.dumps(kwargs)
#     signature = signer.sign(value)
#     return signature
#
#
# def verify_signature(signature, max_age=600):
#     original = signer.unsign(signature, max_age=max_age)
#     logger.debug("original: %s", original)
#     data = json.loads(original)
#     logger.debug("data: %s", data)
#     return data


# def verify_email_code(email, code) -> Tuple[bool, str]:
#     logger.debug("verify_email_code [%s]: %s", code, email)
#     code_from_cache = cache.get(email)
#     logger.debug("code_from_cache: %s", code_from_cache)
#     if not code_from_cache:
#         logger.debug("1 - Code Expired")
#         return False, "Code Expired"
#     if code_from_cache != code:
#         logger.debug("2 - Code Invalid")
#         return False, "Code Invalid"
#     user = AppUser.objects.filter(email=email).first()
#     logger.debug("user: %s", user)
#     if not user:
#         logger.debug("3 - Email Invalid")
#         return False, "Email Invalid"
#     if user.verified:
#         logger.debug("4 - Already Verified")
#         return True, "Already Verified"
#     user.verified = True
#     user.save()
#     return True, "Success"
