import logging
import requests

from bs4 import BeautifulSoup
from random import random
from retrying import retry
from utils.cr_utils import stq_key
from time import sleep


URL = 'https://doi.crossref.org/openurl'


class Matcher:

    def description(self):
        return 'OpenURL Query'

    @retry(wait_exponential_multiplier=1000,
           wait_exponential_max=10000)
    def match(self, reference):
        logging.debug('Matching string {}'.format(reference))
        sleep(5*random())

        query = {'pid': stq_key().get('Mailto'),
                 'redirect': 'false'
                 }
        for oq_key, api_key in [('title', 'series-title'),
                                ('title', 'volume-title'),
                                ('title', 'journal-title'),
                                ('aulast', 'author'),
                                ('volume', 'volume'),
                                ('issue', 'issue'),
                                ('spage', 'first-page'),
                                ('date', 'year'),
                                ('issn', 'ISSN')]:
            if api_key in reference:
                query[oq_key] = reference[api_key]

        with requests.Session() as s:
            r = s.get(URL, params=query)
            result = r.content

        soup = BeautifulSoup(result, 'lxml')
        doi = None
        if soup.find('doi') is not None:
            doi = soup.find('doi').string
        return doi, None
