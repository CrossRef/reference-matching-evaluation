import datetime
import json
import logging
import requests
import time


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
    with open(file_path, 'r') as file:
        data = json.loads(file.read())
    return data


def safe_div(a, b, c):
    if b == 0:
        return c
    return a / b


def keep_fields(item, fields):
    return {k: f for k, f in item.items() if k in fields}
