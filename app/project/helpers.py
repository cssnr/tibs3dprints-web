import secrets
import string


def gen_auth(_bytes: int = 32) -> str:
    return secrets.token_urlsafe(_bytes)


def get_rand(length: int = 30) -> str:
    choices = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(secrets.choice(choices) for _ in range(length))
