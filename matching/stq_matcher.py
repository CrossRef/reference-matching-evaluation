import requests

from bs4 import BeautifulSoup
from utils.cr_utils import stq_key
from urllib.parse import urlparse


STQ_URL = 'https://apps.crossref.org/SimpleTextQuery'


class Matcher:

    def description(self):
        return 'Simple Text Query'

    def match(self, ref_string):
        stq_payload = {'command': 'Submit',
                       'email': stq_key()['Mailto'],
                       'key': stq_key()['Authorization'],
                       'freetext': ref_string}
        with requests.Session() as s:
            r = s.get(STQ_URL)
            r = s.post(STQ_URL, data=stq_payload)
            result = r.content

        soup = BeautifulSoup(result, 'lxml')
        anchors = soup.find_all('a')
        doi = None
        for a in anchors:
            href = a.get('href')
            if href.startswith('https://doi.org/10'):
                doi = urlparse(href).path[1:]
        return doi
