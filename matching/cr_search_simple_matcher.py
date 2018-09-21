import logging
import utils.data_format_keys as dfk

from random import random
from utils.cr_utils import search
from time import sleep


class Matcher:

    def __init__(self, min_score):
        self.min_score = min_score

    def description(self):
        return 'simple Crossref search matcher with minimum score {}' \
                .format(self.min_score)

    def match(self, ref_string):
        logging.debug('Matching string {}'.format(ref_string))
        sleep(random())
        if ref_string is None:
            return None, None
        results = search(ref_string)
        if results is None or not results:
            logging.debug('Searching for string {} got empty results'
                          .format(ref_string))
            return None, None
        if results[0][dfk.CR_ITEM_SCORE] < self.min_score:
            logging.debug('Top hit for string {} has too low score {}'
                          .format(ref_string, results[0][dfk.CR_ITEM_SCORE]))
            return None, None
        logging.debug('String {} matched to DOI {}'
                      .format(ref_string, results[0][dfk.CR_ITEM_DOI]))
        return results[0][dfk.CR_ITEM_DOI], results[0][dfk.CR_ITEM_SCORE]
