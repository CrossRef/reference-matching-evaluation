import datetime
import json
import logging
import re
import requests
import string
import time
import zipfile

from random import choice, randint, random

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'


def init_logging(verbose=False):
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def timestamp():
    return datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()


def remote_call(uri, headers={}):
    logging.debug('Calling {} with headers {}'.format(uri, headers))
    t0 = time.time()
    r = requests.get(uri, headers=headers)
    r.encoding = 'UTF-8'
    t1 = time.time()
    speed = t1 - t0
    code = r.status_code
    return code, speed, str(r.text)


def save_json(data, file_path):
    with open(file_path, 'w+') as file:
        file.write(json.dumps(data, indent=4))


def read_json(file_path):
    if zipfile.is_zipfile(file_path):
        zfile = zipfile.ZipFile(file_path)
        for finfo in zfile.infolist():
            with zfile.open(finfo) as file:
                data = json.loads(file.read())
    else:
        with open(file_path, 'r') as file:
            data = json.loads(file.read())
    return data


def safe_div(a, b, c):
    if b == 0:
        return c
    return a / b


def keep_fields(item, fields):
    if item is None:
        return None
    return {k: f for k, f in item.items() if k in fields}


def add_noise(s):
    if s is None:
        return None
    for _ in range(3):
        if ' ' in s and random() < 0.5:
            pos = choice([m.start() for m in re.finditer(' ', s)])
            s = s[:pos] + s[(pos+1):]
    for _ in range(3):
        if random() < 0.5:
            pos = randint(0, len(s))
            s = s[:pos] + ' ' + s[pos:]
    for _ in range(5):
        if s and random() < 0.3:
            pos = randint(0, len(s)-1)
            letter = choice(list(string.ascii_letters))
            s = s[:pos] + letter + s[(pos+1):]
    return s
