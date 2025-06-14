import secrets
import string


def get_rand(length=30):
    choices = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(secrets.choice(choices) for _ in range(length))
