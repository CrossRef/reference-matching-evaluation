import argparse
import logging
import utils.data_format_keys as dfk

from dataset.generate_strings import read_ref_strings
from matching.match_config import MATCHER
from multiprocessing import Pool
from utils.utils import init_logging, save_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run a citation matcher')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-d', '--dataset', required=True, type=str)
    parser.add_argument('-o', '--output', required=True, type=str)

    args = parser.parse_args()

    init_logging(args.verbose)

    dataset = read_ref_strings(args.dataset)

    logging.info('Matching with matcher: {}'.format(MATCHER.description()))
    with Pool() as p:
        results = p.map(MATCHER.match,
                        [item[dfk.DATASET_REF_STRING] for item in dataset])

    [d.update({dfk.DATASET_DOI_TEST: r,
               dfk.DATASET_MATCHER: MATCHER.description()})
        for r, d in zip(results, dataset)]
    save_json(dataset, args.output)
    logging.info('Matched dataset saved in {}'.format(args.output))
