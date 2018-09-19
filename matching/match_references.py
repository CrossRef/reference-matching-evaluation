import argparse
import logging
import utils.data_format_keys as dfk

from dataset.generate_dataset import keep_fields, read_dataset, save_dataset
from matching.match_config import MATCHER
from multiprocessing import Pool
from utils.cr_utils import get_item
from utils.utils import init_logging

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run a citation matcher')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-d', '--dataset', required=True, type=str)
    parser.add_argument('-o', '--output', required=True, type=str)

    args = parser.parse_args()

    init_logging(args.verbose)

    dataset = read_dataset(args.dataset)

    logging.info('Matching with matcher: {}'.format(MATCHER.description()))
    with Pool() as p:
        results = p.map(MATCHER.match,
                        [item[dfk.DATASET_REF_STRING] for item in dataset])

    [d.update({dfk.DATASET_TARGET_TEST: {dfk.CR_ITEM_DOI: r},
               dfk.DATASET_MATCHER: MATCHER.description()})
        for r, d in zip(results, dataset)]
    for d in dataset:
        if d[dfk.DATASET_TARGET_TEST][dfk.CR_ITEM_DOI] is not None:
            item = get_item(d[dfk.DATASET_TARGET_TEST][dfk.CR_ITEM_DOI])
            item = keep_fields(item, d[dfk.DATASET_TARGET_GT].keys())
            d[dfk.DATASET_TARGET_TEST] = item
    save_dataset(dataset, args.output)
    logging.info('Matched dataset saved in {}'.format(args.output))
