import secrets
import string
from typing import List, Optional

from django.core.validators import validate_ipv46_address


def gen_auth(_bytes: int = 32) -> str:
    return secrets.token_urlsafe(_bytes)


def get_rand(length: int = 32) -> str:
    choices = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(secrets.choice(choices) for _ in range(length))


def get_ipaddress(request) -> Optional[str]:
    keys = [
        "X_FORWARDED_FOR",
        "HTTP_X_FORWARDED_FOR",
        "HTTP_CLIENT_IP",
        "HTTP_X_REAL_IP",
        "HTTP_X_FORWARDED",
        "HTTP_X_CLUSTER_CLIENT_IP",
        "HTTP_FORWARDED_FOR",
        "HTTP_FORWARDED",
        "HTTP_CF_CONNECTING_IP",
        "X-CLIENT-IP",
        "X-REAL-IP",
        "X-CLUSTER-CLIENT-IP",
        "X_FORWARDED",
        "FORWARDED_FOR",
        "CF-CONNECTING-IP",
        "TRUE-CLIENT-IP",
        "FASTLY-CLIENT-IP",
        "FORWARDED",
        "CLIENT-IP",
    ]
    results: List[str] = [value for key in keys if (value := request.META.get(key))]
    if not results:
        return None
    for result in results:
        try:
            if "," in result:
                result = result.split(",")[0]
            validate_ipv46_address(result)
            return result
        except Exception:
            continue  # nosec
