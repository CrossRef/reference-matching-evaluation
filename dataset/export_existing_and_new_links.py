import argparse
import config
import logging
import matching.cr_search_validation_matcher
import matching.stq_matcher
import utils.data_format_keys as dfk

from multiprocessing import Pool
from random import sample
from utils.utils import init_logging, read_json, save_json


def is_unstructured(ref):
    return dfk.CR_ITEM_UNSTRUCTURED in ref


def is_structured(ref):
    return not is_unstructured(ref)


def extract_refs(sample_works, filter_fun=is_unstructured):
    references = []
    for work in sample_works.get(dfk.SAMPLE_SAMPLE):
        source_doi = work.get(dfk.CR_ITEM_DOI)
        for ref in work.get(dfk.CR_ITEM_REFERENCE, []):
            if ref.get(dfk.CR_ITEM_DOI_ASSERTED_BY) != 'publisher' \
                    and filter_fun(ref):
                ref['source_DOI'] = source_doi
                references.append(ref)
    return references


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='analyze a sample file')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-s', '--sample', type=str, required=True)
    parser.add_argument('-n', '--references', type=int)
    parser.add_argument('-p', '--parsed', action='store_true')
    parser.add_argument('-o', '--output', type=str, required=True)

    args = parser.parse_args()

    init_logging(args.verbose)

    sample_data = read_json(args.sample)

    if args.parsed:
        references = extract_refs(sample_data, filter_fun=is_structured)
    else:
        references = extract_refs(sample_data, filter_fun=is_unstructured)
    logging.info('Total number of references: {}'.format(len(references)))

    if args.references is not None:
        references = sample(references, args.references)

    logging.info('Sampled number of references: {}'.format(len(references)))

    matcher = matching.cr_search_validation_matcher.Matcher(0.4, -1)
    with Pool(config.THREADS) as p:
        api_results = p.map(matcher.match, references)

    matcher = matching.stq_matcher.Matcher()
    with Pool(config.THREADS) as p:
        stq_results = p.map(matcher.match, references)

    save_json([{'source_DOI': r.get('source_DOI', '').lower(),
                'reference': r,
                'original_link': r.get(dfk.CR_ITEM_DOI, '').lower()
                if r.get(dfk.CR_ITEM_DOI_ASSERTED_BY) == 'crossref'
                else None,
                'current_STQ_link': s[0] if s[0] is None else s[0].lower(),
                'search_API_link': a[0] if a[0] is None else a[0].lower(),
                'search_API_score': a[1]}
               for r, s, a in zip(references, stq_results, api_results)],
              args.output)
