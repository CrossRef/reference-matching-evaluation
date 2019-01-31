import argparse
import config
import logging
import matching.cr_search_validation_matcher
import matching.stq_matcher
import matching.openurl_query_matcher
import utils.data_format_keys as dfk

from multiprocessing import Pool
from random import sample
from utils.utils import init_logging, read_json, save_json


def is_unstructured(ref):
    return ref.get(dfk.CR_ITEM_DOI_ASSERTED_BY) != 'publisher' \
        and dfk.CR_ITEM_UNSTRUCTURED in ref


def is_structured(ref):
    return not is_unstructured(ref)


def always(ref):
    return True


def extract_refs(sample_works, filter_fun=always):
    references = []
    for work in sample_works.get(dfk.SAMPLE_SAMPLE):
        source_doi = work.get(dfk.CR_ITEM_DOI)
        for ref in work.get(dfk.CR_ITEM_REFERENCE, []):
            if filter_fun(ref):
                ref['source_DOI'] = source_doi
                references.append(ref)
    return references


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='export a sample of references and matches')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-s', '--sample', type=str, required=True)
    parser.add_argument('-n', '--references', type=int)
    parser.add_argument('-p', '--parsed', action='store_true')
    parser.add_argument('-u', '--unparsed', action='store_true')
    parser.add_argument('-j', '--journalfile', type=str)
    parser.add_argument('-o', '--output', type=str, required=True)

    args = parser.parse_args()

    init_logging(args.verbose)

    sample_data = read_json(args.sample)

    if args.parsed:
        references = extract_refs(sample_data, filter_fun=is_structured)
    elif args.unparsed:
        references = extract_refs(sample_data, filter_fun=is_unstructured)
    else:
        references = extract_refs(sample_data)
    logging.info('Total number of references: {}'.format(len(references)))

    if args.references is not None:
        references = sample(references, args.references)

    logging.info('Sampled number of references: {}'.format(len(references)))

    data = [{'source_DOI': r.get('source_DOI', '').lower(),
             'reference': r,
             'publisher_link': r.get(dfk.CR_ITEM_DOI, '').lower()
             if r.get(dfk.CR_ITEM_DOI_ASSERTED_BY) == 'publisher'
             else None,
             'open_url': None,
             'sbmv_structured': None,
             'simple_text_query': None,
             'sbmv_unstructured': None}
            for r in references]

    journal_file = None
    if args.journalfile is not None:
        journal_file = args.journalfile
    matcher = matching.cr_search_validation_matcher.Matcher(
        0.4, -1, journal_file=journal_file)

    refs_structured = [d for d in data if d['publisher_link'] is None]
    with Pool(config.THREADS) as p:
        results = p.map(matcher.match,
                        [r['reference'] for r in refs_structured])
    [d.update({'sbmv_structured': {'DOI': r[0], 'score': r[1]}})
     for d, r in zip(refs_structured, results)]

    refs_unstructured = [d for d in data
                         if d['publisher_link'] is None
                         and 'unstructured' in d['reference']]
    with Pool(config.THREADS) as p:
        results = p.map(matcher.match,
                        [r['reference']['unstructured']
                         for r in refs_unstructured])
    [d.update({'sbmv_unstructured': {'DOI': r[0], 'score': r[1]}})
     for d, r in zip(refs_unstructured, results)]

    matcher = matching.openurl_query_matcher.Matcher()
    with Pool(config.THREADS) as p:
        results = p.map(matcher.match,
                        [r['reference'] for r in refs_structured])
    [d.update({'open_url': r[0]}) for d, r in zip(refs_structured, results)]

    matcher = matching.stq_matcher.Matcher()
    with Pool(config.THREADS) as p:
        results = p.map(matcher.match,
                        [r['reference']['unstructured']
                         for r in refs_unstructured])
    [d.update({'simple_text_query': r[0]})
     for d, r in zip(refs_unstructured, results)]

    [d.update({'gt': ''}) for d in data]

    save_json(data, args.output)
