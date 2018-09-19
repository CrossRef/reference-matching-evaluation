import json
import logging
import re
import urllib.parse

from functools import lru_cache
from habanero import Crossref
from multiprocessing import Pool
from pathlib import Path
from utils.utils import remote_call

BASE_URL = 'https://api.crossref.org'
CN_BASE_URL = 'http://data.crossref.org'

SAMPLE_CHUNK_SIZE = 100

CRAPI_KEY_FN = '.crapi_key'
STQ_KEY_FN = '.stq_key'


def crapi_key():
    return load_key(CRAPI_KEY_FN)


def stq_key():
    return load_key(STQ_KEY_FN)


@lru_cache(maxsize=None)
def load_key(key):
    with open(Path.home() / key, mode='r') as kf:
        key_value = kf.read()
    return json.loads(key_value)


API_KEY = crapi_key()['Authorization']
POLITE = crapi_key()['Mailto']


def get_sample_chunk(size, filter={}, query={}):
    return Crossref(base_url=BASE_URL, mailto=POLITE, api_key=API_KEY) \
        .works(sample=size, filter=filter, query=query)['message']['items']


def generate_sample_args(size=0, filter={}, query={}):
    sample_count = int(size / SAMPLE_CHUNK_SIZE)
    sizes = [SAMPLE_CHUNK_SIZE] * sample_count
    if size % SAMPLE_CHUNK_SIZE != 0:
        sizes.append(size % SAMPLE_CHUNK_SIZE)
    return [(s, filter, query) for s in sizes]


def get_sample(size=100, filter={}, query={}):
    args = locals()
    results = []
    with Pool() as pool:
        results = pool.starmap(get_sample_chunk, generate_sample_args(**args))
    results = [item for sublist in results for item in sublist]
    return results


def parse_filter_text(filter_text):
    return {f.split(':')[0]: f.split(':')[1]
            for f in filter_text.split(',')}


def create_ref_string(doi, style):
    headers = {'Accept': 'text/x-bibliography; style={}'.format(style)}
    code, _, ref_string = remote_call('{}/{}'.format(CN_BASE_URL, doi),
                                      headers)
    if code != 200:
        logging.error(
            'Creating ref string in style {} for DOI {} failed with code {}'.
            format(style, doi, code))
        return None
    for rem in ['doi\:10\..*',
                'Available at: http://dx.doi.org/.*',
                'Crossref. Web.']:
        ref_string = re.sub(rem, '', ref_string)
    ref_string = re.sub('\n', ' ', ref_string)
    ref_string = re.sub(' +', ' ', ref_string)
    return ref_string.strip()


def search(string):
    if string is None:
        return None
    headers = crapi_key()
    query = '{}/works?query.bibliographic={}' \
        .format(BASE_URL, urllib.parse.quote(string, safe=''))
    code, _, result = remote_call(query, headers=headers)
    if code != 200:
        logging.error('Searching for string {} failed with code {}'.
                      format(string, code))
        return None
    result_message = json.loads(result)['message']
    if 'items' in result_message:
        return result_message['items']
    return None


def get_item(doi):
    if doi is None:
        return None
    headers = crapi_key()
    query = '{}/works/{}'.format(BASE_URL, urllib.parse.quote(doi, safe=''))
    code, _, result = remote_call(query, headers=headers)
    if code != 200:
        logging.error('Getting item {} failed with code {}'.
                      format(doi, code))
        return None
    result_message = json.loads(result)['message']
    return result_message
