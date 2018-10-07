import argparse
import config
import logging
import utils.data_format_keys as dfk

from dataset.generate_dataset import read_dataset, save_dataset
from matching.match_config import MATCHER
from multiprocessing import Pool
from utils.cr_utils import get_item
from utils.utils import init_logging, keep_fields

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run a citation matcher')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-d', '--dataset', required=True, type=str)
    parser.add_argument('-o', '--output', required=True, type=str)

    args = parser.parse_args()

    init_logging(args.verbose)

    dataset_data = read_dataset(args.dataset)
    dataset = dataset_data[dfk.DATASET_DATASET]

    logging.info('Matching with matcher: {}'.format(MATCHER.description()))
    with Pool(config.THREADS) as p:
        results = p.map(MATCHER.match,
                        [item[dfk.DATASET_REF_STRING] for item in dataset])

    [d.update({dfk.DATASET_TARGET_TEST:
               {dfk.CR_ITEM_DOI: None if r[0] is None else r[0].lower()},
               dfk.DATASET_MATCHER: MATCHER.description(),
               dfk.DATASET_SCORE: r[1]})
        for r, d in zip(results, dataset)]
    for d in dataset:
        if d[dfk.DATASET_TARGET_TEST][dfk.CR_ITEM_DOI] is not None:
            item = get_item(d[dfk.DATASET_TARGET_TEST][dfk.CR_ITEM_DOI])
            item = keep_fields(item, d[dfk.DATASET_TARGET_GT].keys())
            d[dfk.DATASET_TARGET_TEST] = item

    dataset_data = {dfk.DATASET_DOIS: dataset_data[dfk.DATASET_DOIS],
                    dfk.DATASET_DATASET: dataset}
    save_dataset(dataset_data, args.output)
