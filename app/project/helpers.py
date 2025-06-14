import random
import string


def get_rand(length=30):
    choices = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choices(choices, k=length))
