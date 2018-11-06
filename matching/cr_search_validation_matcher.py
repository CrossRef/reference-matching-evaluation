import logging
import re
import utils.data_format_keys as dfk
import unidecode

from fuzzywuzzy import fuzz
from random import random
from utils.cr_utils import search
from time import sleep


class Matcher:

    def __init__(self, min_score, min_similarity, excluded_dois=[]):
        self.excluded_dois = [d.lower() for d in excluded_dois]
        self.min_score = min_score
        self.min_similarity = min_similarity

    def description(self):
        return ('Crossref search matcher with validation ' +
                'and minimum normalized relevance score {} ' +
                'and minimum candidate similarity {}') \
                .format(self.min_score, self.min_similarity)

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

        candidates = []
        for result in results:
            if result.get(dfk.CR_ITEM_DOI).lower() in self.excluded_dois:
                continue
            if result.get(dfk.CR_ITEM_SCORE)/len(ref_string) >= self.min_score:
                candidates.append(result)
            else:
                break

        chosen, similarity = self.choose_best(candidates, ref_string)
        if chosen is None:
            return None, None
        if similarity < self.min_similarity:
            return None, None

        return chosen.get(dfk.CR_ITEM_DOI), similarity

    def choose_best(self, candidates, ref_string):
        if not candidates:
            return None, None
        similarities = [self.similarity(c, ref_string) for c in candidates]
        if max(similarities) == 0:
            return None, None
        return candidates[similarities.index(max(similarities))], \
            max(similarities)

    def similarity(self, candidate, ref_string):
        # weights for generalized jaccard similarity
        cand_set = {}
        str_set = {}

        # weights of relevalnce score
        cand_set['score'] = candidate['score']/100
        str_set['score'] = max(1, candidate['score']/100)

        # weights of normalized relevance score
        cand_set['score_norm'] = candidate['score']/len(ref_string)
        str_set['score_norm'] = max(1, candidate['score']/len(ref_string))

        # remove DOI and arXiv from reference string
        # this is done to leave only bibliographic numbers in the strings
        # all additional numbers present in the string lower the similarity
        ref_string = re.sub('(?<!\d)10\.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+', '',
                            ref_string)
        ref_string = re.sub('(?<![a-zA-Z0-9])arXiv:[\d\.]+', '', ref_string)
        ref_string = re.sub('\[[^\[\]]*\]', '', ref_string)

        # complete last page if abbreviated
        # changes "1425-37" to "1425-1437"
        for pages in re.findall('\d+[\u002D\u00AD\u2010\u2011\u2012\u2013' +
                                '\u2014\u2015\u207B\u208B\u2212-]\d+',
                                ref_string):
            numbers = re.findall('(?<!\d)\d+(?!\d)', pages)
            first = numbers[0]
            last = numbers[1]
            if len(first) > len(last) and int(first[-len(last):]) <= int(last):
                last = first[:(len(first)-len(last))] + last
                ref_string = re.sub(pages, first + '-' + last, ref_string)

        # all number appearing in the ref string
        ref_numbers = re.findall('(?<!\d)\d+(?!\d)', ref_string[5:])
        if not ref_numbers:
            return 0

        # if volume equals year, but only one instance is present
        # in the reference string, add another copy
        issued = candidate['issued']['date-parts']
        if 'volume' in candidate and issued is not None and \
                issued[0][0] is not None and \
                candidate['volume'] == str(issued[0][0]) and \
                ref_numbers.count(candidate['volume']) == 1:
            ref_numbers.append(candidate['volume'])

        # weights of volume
        if 'volume' in candidate:
            self.update_weights('volume', candidate['volume'], ref_numbers,
                                cand_set, str_set)

        # weights for year
        if issued is not None and issued[0][0] is not None:
            self.update_weights('year', str(issued[0][0]), ref_numbers,
                                cand_set, str_set)

        # weights for issue
        if 'issue' in candidate:
            self.update_weights('issue', candidate['issue'], ref_numbers,
                                cand_set, str_set)

        # weights for pages
        if 'page' in candidate:
            self.update_weights('page', candidate['page'], ref_numbers,
                                cand_set, str_set)

        # weights for title
        if 'title' in candidate and candidate['title']:
            self.update_weights('title', candidate['title'][0], ref_numbers,
                                cand_set, str_set)

        # weights for container-title
        if 'container-title' in candidate and candidate['container-title']:
            self.update_weights('ctitle', candidate['container-title'][0],
                                ref_numbers, cand_set, str_set)

        # weights for author
        if 'author' in candidate and candidate['author'] \
                and 'family' in candidate['author'][0]:
            a = unidecode.unidecode(candidate['author'][0]['family']).lower()
            b = unidecode.unidecode(ref_string).lower()[:(2*len(a))]
            cand_set['author'] = 1
            str_set['author'] = fuzz.partial_ratio(a, b) / 100

        # if the year wasn't found, try with year +- 1
        if issued is not None and issued[0][0] is not None and \
                str_set['year_0'] == 0:
            if str(issued[0][0]-1) in ref_numbers:
                str_set['year_0'] = 0.5
                ref_numbers.remove(str(issued[0][0]-1))
            elif str(issued[0][0]+1) in ref_numbers:
                str_set['year_0'] = 0.5
                ref_numbers.remove(str(issued[0][0]+1))

        # weights for the remaining numbers in the ref string
        for i, r in enumerate(ref_numbers):
            cand_set['rest_'+str(i)] = 0
            str_set['rest_'+str(i)] = 1

        # generalized Jaccard similarity
        num = sum([min(cand_set[n], str_set[n]) for n in cand_set.keys()])
        den = sum([max(cand_set[n], str_set[n]) for n in cand_set.keys()])
        if den == 0:
            return 1
        return num/den

    def update_weights(self, name, cand_str, ref_numbers, cand_set, str_set,
                       weight=1):
        for i, number in enumerate(re.findall('(?<!\d)\d+(?!\d)', cand_str)):
            cand_set[name + '_' + str(i)] = weight
            str_set[name + '_' + str(i)] = 0
            if number in ref_numbers:
                str_set[name + '_' + str(i)] = weight
                ref_numbers.remove(number)
