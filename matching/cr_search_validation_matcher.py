import logging
import re
import utils.data_format_keys as dfk
import unidecode

from evaluation.evaluation_utils import doi_normalize
from fuzzywuzzy import fuzz
from random import random
from utils.cr_utils import search, generate_unstructured
from time import sleep


class Matcher:

    def __init__(self, min_score, min_similarity, excluded_dois=[],
                 journal_file=None):
        self.excluded_dois = [doi_normalize(d) for d in excluded_dois]
        self.min_score = min_score
        self.min_similarity = min_similarity
        self.journal_abbrev = {}
        if journal_file is not None:
            with open(journal_file) as f:
                content = f.readlines()
            content = [x.strip().split('\t') for x in content]
            self.journal_abbrev = {l[0]: l[1] for l in content}

    def description(self):
        return ('Crossref search matcher with validation ' +
                'and minimum normalized relevance score {} ' +
                'and minimum candidate similarity {}') \
                .format(self.min_score, self.min_similarity)

    def match(self, reference):
        if isinstance(reference, str):
            return self.match_string(reference)
        return self.match_structured(reference)

    def match_string(self, ref_string):
        if not ref_string.strip():
            ref_string = None
        return self.match_object(ref_string, lambda s: s,
                                 self.similarity_unstructured, 20)

    def match_structured(self, reference):
        candidate, score = self.match_object(reference, generate_unstructured,
                                             self.similarity_structured, 100)

        journal_norm = re.sub('[^a-z]', '',
                              reference.get('journal-title', '').lower())
        if 'journal-title' in reference \
                and journal_norm in self.journal_abbrev:
            reference['journal-title'] = self.journal_abbrev[journal_norm]
            candidate_j, score_j = \
                self.match_object(reference, generate_unstructured,
                                  self.similarity_structured, 100)
            if score_j > score:
                return candidate_j, score_j
        return candidate, score

    def match_object(self, reference, get_query, similarity, rows):
        ref_string = get_query(reference)

        sleep(random())
        results = search(ref_string, rows=rows)
        if results is None or not results:
            logging.debug('Searching for string {} got empty results'
                          .format(ref_string))
            return None, None

        candidates = self.select_candidates(ref_string, results)

        return self.choose_best(candidates, reference,
                                similarity, self.min_similarity)

    def select_candidates(self, ref_string, results):
        candidates = []
        for result in results:
            if doi_normalize(result.get(dfk.CR_ITEM_DOI)) \
                    in self.excluded_dois:
                continue
            if not candidates:
                candidates.append(result)
            elif result.get(dfk.CR_ITEM_SCORE)/len(ref_string) >= \
                    self.min_score:
                candidates.append(result)
            else:
                break
        return candidates

    def choose_best(self, candidates, ref_string, sim_fun, min_similarity):
        if not candidates:
            return None, None
        similarities = [sim_fun(c, ref_string) for c in candidates]
        if max(similarities) < min_similarity:
            return None, None
        return candidates[similarities.index(max(similarities))] \
            .get(dfk.CR_ITEM_DOI), \
            max(similarities)

    def similarity_unstructured(self, candidate, ref_string):
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
        ref_string = re.sub('\[[^\[\]]*\]', '', ref_string).strip()

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
            self.update_weights_all('volume', candidate['volume'], ref_numbers,
                                    cand_set, str_set)

        # weights for year
        if issued is not None and issued[0][0] is not None:
            self.update_weights_all('year', str(issued[0][0]), ref_numbers,
                                    cand_set, str_set)

        # weights for issue
        if 'issue' in candidate:
            self.update_weights_all('issue', candidate['issue'], ref_numbers,
                                    cand_set, str_set)

        # weights for pages
        if 'page' in candidate:
            self.update_weights_all('page', candidate['page'], ref_numbers,
                                    cand_set, str_set)

        # weights for title
        if 'title' in candidate and candidate['title']:
            self.update_weights_all('title', candidate['title'][0],
                                    ref_numbers, cand_set, str_set)

        # weights for container-title
        if 'container-title' in candidate and candidate['container-title']:
            self.update_weights_all('ctitle', candidate['container-title'][0],
                                    ref_numbers, cand_set, str_set)

        # weights for author
        if 'author' in candidate and candidate['author'] \
                and 'family' in candidate['author'][0]:
            a = unidecode.unidecode(candidate['author'][0]['family']).lower()
            b = unidecode.unidecode(ref_string).lower()[:(3*len(a))]
            cand_set['author'] = 1
            str_set['author'] = fuzz.partial_ratio(a, b) / 100
        elif 'editor' in candidate and candidate['editor'] \
                and 'family' in candidate['editor'][0]:
            a = unidecode.unidecode(candidate['editor'][0]['family']).lower()
            b = unidecode.unidecode(ref_string).lower()[:(3*len(a))]
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

        support = 0
        if 'title' in candidate and candidate['title']:
            a = unidecode.unidecode(candidate['title'][0]).lower()
            b = unidecode.unidecode(ref_string).lower()
            if fuzz.partial_ratio(a, b) / 100 > 0.7:
                support = support + 1
        for k, v in str_set.items():
            if k == 'year_0' and v > 0:
                support = support + 1
            if k == 'volume_0' and v == 1:
                support = support + 1
            if k == 'author' and v > 0.7:
                support = support + 1
            if k == 'page_0' and v == 1:
                support = support + 1
        if support < 3:
            return 0

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

    def similarity_structured(self, candidate, ref):
        # weights for generalized jaccard similarity
        cand_set = {}
        str_set = {}

        # weights of volume
        if ref.get('volume', ''):
            self.update_weights_one('volume', candidate.get('volume', ''),
                                    ref.get('volume', ''), cand_set, str_set)

        # weights for year
        year = ''
        issued = candidate['issued']['date-parts']
        if issued is not None and issued[0][0] is not None:
            year = str(issued[0][0])
        if ref.get('year', ''):
            self.update_weights_one('year', year, ref.get('year', ''),
                                    cand_set, str_set)
            if 'year' in str_set and str_set['year'] < 1 and year \
                    and ref.get('year', ''):
                try:
                    year1 = int(year)
                    year2 = int(ref.get('year', ''))
                    if year1 + 1 == year2 or year2 + 1 == year1:
                        str_set['year'] = 0.5
                except ValueError:
                    pass

        # weights for pages
        if ref.get('first-page', ''):
            self.update_weights_one('page', candidate.get('page', ''),
                                    ref.get('first-page', ''),
                                    cand_set, str_set)

        # weights for title
        if ref.get('article-title', ''):
            a = unidecode.unidecode(candidate.get('title', [''])[0]).lower()
            b = unidecode.unidecode(ref.get('article-title', '')).lower()
            cand_set['title'] = 1
            str_set['title'] = fuzz.ratio(a, b) / 100

        # weights for container-title
        if ref.get('journal-title', ''):
            a = unidecode.unidecode(candidate.get('container-title', [''])[0])
            a = a.lower()
            b = unidecode.unidecode(ref.get('journal-title', '')).lower()
            cand_set['ctitle'] = 1
            str_set['ctitle'] = fuzz.ratio(a, b) / 100

        # weights for volume-title
        if ref.get('volume-title', ''):
            a = unidecode.unidecode(candidate.get('title', [''])[0])
            a = a.lower()
            b = unidecode.unidecode(ref.get('volume-title', '')).lower()
            cand_set['vtitle'] = 1
            str_set['vtitle'] = fuzz.ratio(a, b) / 100

        # weights for author
        if ref.get('author', ''):
            a = ''
            if 'author' in candidate and candidate['author'] \
                    and 'family' in candidate['author'][0]:
                a = unidecode.unidecode(candidate['author'][0]['family'])
                a = a.lower()
            b = unidecode.unidecode(ref.get('author', '')).lower()
            ratio_author = fuzz.ratio(a, b)
            a = ''
            if 'editor' in candidate and candidate['editor'] \
                    and 'family' in candidate['editor'][0]:
                a = unidecode.unidecode(candidate['editor'][0]['family'])
                a = a.lower()
            ratio_editor = fuzz.ratio(a, b)
            cand_set['author'] = 1
            str_set['author'] = max(ratio_author, ratio_editor) / 100

        print(candidate['DOI'])
        print(cand_set)
        print(str_set)

        support = 0
        for k, v in str_set.items():
            if k == 'title' and v > 0.7:
                support = support + 1
            if k == 'ctitle' and v > 0.7:
                support = support + 1
            if k == 'vtitle' and v > 0.7:
                support = support + 1
            if k == 'author' and v > 0.7:
                support = support + 1
        if support < 1:
            return 0
        support = 0
        for k, v in str_set.items():
            if k == 'year' and v > 0 and cand_set[k] > 0:
                support = support + 1
            if k == 'volume' and v == 1 and cand_set[k] > 0:
                support = support + 1
            if k == 'title' and v > 0.7:
                support = support + 1
            if k == 'ctitle' and v > 0.7:
                support = support + 1
            if k == 'vtitle' and v > 0.7:
                support = support + 1
            if k == 'author' and v > 0.7:
                support = support + 1
            if k == 'page' and v == 1 and cand_set[k] > 0:
                support = support + 1
        if support < 3:
            return 0
        if candidate.get('type') == 'book-chapter' and 'first-page' not in ref:
            return 0
        if candidate.get('type') == 'journal-issue':
            return 0

        # generalized Jaccard similarity
        num = sum([min(cand_set[n], str_set[n]) for n in cand_set.keys()])
        den = sum([max(cand_set[n], str_set[n]) for n in cand_set.keys()])
        if den == 0:
            return 1
        return num/den

    def update_weights_all(self, name, cand_str, ref_numbers, cand_set,
                           str_set, weight=1):
        for i, number in enumerate(re.findall('(?<!\d)\d+(?!\d)', cand_str)):
            cand_set[name + '_' + str(i)] = weight
            str_set[name + '_' + str(i)] = 0
            if number in ref_numbers:
                str_set[name + '_' + str(i)] = weight
                ref_numbers.remove(number)

    def update_weights_one(self, name, cand_str, ref_str, cand_set, ref_set,
                           weight=1):
        cand = re.search('(?<!\d)\d+(?!\d)', cand_str)
        ref = re.search('(?<!\d)\d+(?!\d)', ref_str)
        if cand is not None and ref is not None:
            cand = cand.group(0)
            ref = ref.group(0)
            cand_set[name] = weight
            ref_set[name] = 0
            if cand == ref:
                ref_set[name] = weight
        else:
            cand_set[name] = weight/2
            ref_set[name] = 0
