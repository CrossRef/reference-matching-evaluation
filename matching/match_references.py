import argparse
import config
import logging
import utils.data_format_keys as dfk

from dataset.generate_dataset import read_dataset, save_dataset
from matching.match_config import MATCHER
from multiprocessing import Pool
from utils.cr_utils import get_item
from utils.utils import init_logging, keep_fields


def transform(item):
    fields = list(item.get(dfk.DATASET_TARGET_GT, {}).keys())
    if fields == ['DOI']:
        return item[dfk.DATASET_TARGET_TEST]
    if item.get(dfk.DATASET_TARGET_TEST, {}).get(dfk.CR_ITEM_DOI) is None:
        return item[dfk.DATASET_TARGET_TEST]
    r_item = get_item(item.get(dfk.DATASET_TARGET_TEST, {})
                      .get(dfk.CR_ITEM_DOI))
    if r_item is not None:
        return keep_fields(r_item, item.get(dfk.DATASET_TARGET_GT, {}).keys())
    return item[dfk.DATASET_TARGET_TEST]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run a citation matcher')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-d', '--dataset', required=True, type=str)
    parser.add_argument('-o', '--output', required=True, type=str)

    args = parser.parse_args()

    init_logging(args.verbose)

    dataset_data = read_dataset(args.dataset)
    dataset = dataset_data.get(dfk.DATASET_DATASET)

    logging.info('Matching with matcher: {}'.format(MATCHER.description()))
    if dfk.DATASET_REF_STRING in dataset[0]:
        with Pool(config.THREADS) as p:
            results = p.map(MATCHER.match,
                            [item.get(dfk.DATASET_REF_STRING)
                             for item in dataset])
    else:
        with Pool(config.THREADS) as p:
            results = p.map(MATCHER.match,
                            [item.get(dfk.DATASET_REFERENCE)
                             for item in dataset])

    [d.update({dfk.DATASET_TARGET_TEST:
               {dfk.CR_ITEM_DOI: None if r[0] is None else r[0].lower()},
               dfk.DATASET_MATCHER: MATCHER.description(),
               dfk.DATASET_SCORE: r[1]})
        for r, d in zip(results, dataset)]

    with Pool(config.THREADS) as p:
        transformed = p.map(transform, dataset)
    [d.update({dfk.DATASET_TARGET_TEST: t})
        for t, d in zip(transformed, dataset)]

    dataset_data = {dfk.DATASET_DOIS: dataset_data.get(dfk.DATASET_DOIS),
                    dfk.DATASET_DATASET: dataset}
    save_dataset(dataset_data, args.output)
