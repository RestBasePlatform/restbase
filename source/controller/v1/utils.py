import hashlib
import random
import datetime


def generate_secret_token():
    seed = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    return hashlib.md5((seed + str(random.randint(1, 1000))).encode()).hexdigest()
