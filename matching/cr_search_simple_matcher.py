import logging
import utils.data_format_keys as dfk

from evaluation.evaluation_utils import doi_normalize
from random import random
from utils.cr_utils import search
from time import sleep


class Matcher:

    def __init__(self, min_score, excluded_dois=[]):
        self.excluded_dois = [doi_normalize(d) for d in excluded_dois]
        self.min_score = min_score

    def description(self):
        return 'Crossref search matcher with DOI exclusion ' + \
                'and minimum score {}'.format(self.min_score)

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
        for result in results:
            if doi_normalize(result.get(dfk.CR_ITEM_DOI)) \
                    in self.excluded_dois:
                logging.debug('String {} NOT matched to excluded DOI {}'
                              .format(ref_string, result.get(dfk.CR_ITEM_DOI)))
                continue
            if result.get(dfk.CR_ITEM_SCORE) < self.min_score:
                logging.debug('Top hit for string {} has too low score {}'
                              .format(ref_string,
                                      result.get(dfk.CR_ITEM_SCORE)))
                return None, None
            logging.debug('String {} matched to DOI {}'
                          .format(ref_string, result.get(dfk.CR_ITEM_DOI)))
            return result.get(dfk.CR_ITEM_DOI), result.get(dfk.CR_ITEM_SCORE)
        return None, None
