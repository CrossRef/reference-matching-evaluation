import logging
import re
import utils.data_format_keys as dfk

from evaluation.evaluation_utils import doi_normalize
from random import random
from utils.cr_utils import search, generate_unstructured
from time import sleep


class Matcher:

    def __init__(self, min_score, excluded_dois=[], journal_file=None):
        self.excluded_dois = [doi_normalize(d) for d in excluded_dois]
        self.min_score = min_score
        self.journal_abbrev = {}
        if journal_file is not None:
            with open(journal_file) as f:
                content = f.readlines()
                content = [x.strip().split('\t') for x in content]
                self.journal_abbrev = {l[0]: l[1] for l in content}

    def description(self):
        return 'Crossref search matcher with DOI exclusion ' + \
                'and minimum score {}'.format(self.min_score)

    def match(self, reference):
        if isinstance(reference, str):
            return self.match_string(reference)
        return self.match_structured(reference)

    def match_structured(self, reference):
        candidate, score = self.match_string(generate_unstructured(reference))

        journal_norm = re.sub('[^a-z]', '',
                              reference.get('journal-title', '').lower())
        if 'journal-title' in reference and \
                journal_norm in self.journal_abbrev:
            reference['journal-title'] = self.journal_abbrev[journal_norm]
            candidate_j, score_j = \
                self.match_string(generate_unstructured(reference))
            if score_j > score:
                return candidate_j, score_j
        return candidate, score

    def match_string(self, ref_string):
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
