import argparse
import config
import itertools
import logging
import utils.data_format_keys as dfk

from dataset.custom_styles import CUSTOM_STYLES
from dataset.draw_sample import read_sample_data
from multiprocessing import Pool
from utils.cr_utils import create_ref_string
from utils.utils import add_noise, init_logging, keep_fields, read_json, \
    save_json


def save_dataset(ref_strings, file_path):
    save_json(ref_strings, file_path)
    logging.info('Dataset written to {}'.format(file_path))


def read_dataset(file_path):
    return read_json(file_path)


def generate_target_gt(item, fields):
    target = keep_fields(item, fields + [dfk.CR_ITEM_DOI])
    target[dfk.CR_ITEM_DOI] = item.get(dfk.CR_ITEM_DOI, '').lower()
    return target


def format_ref_string(item, style):
    if style in CUSTOM_STYLES:
        return CUSTOM_STYLES.get(style)(item)
    else:
        return create_ref_string(item.get(dfk.CR_ITEM_DOI), style)


def generate_dataset(sample, styles, fields):
    logging.info('Generating dataset')
    prod_sample_style = list(itertools.product(sample, styles))
    with Pool(config.THREADS) as p:
        results = p.starmap(format_ref_string, prod_sample_style)
    return [{dfk.DATASET_STYLE: ds[1],
             dfk.DATASET_REF_STRING: r,
             dfk.DATASET_TARGET_GT: generate_target_gt(ds[0], fields)}
            for ds, r in zip(prod_sample_style, results)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='create a simple evaluation dataset')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-l', '--styles',
                        help='comma-separated list of citation style names',
                        type=str, default='apa')
    parser.add_argument('-d', '--distort',
                        help='add random noise to strings',
                        action='store_true')
    parser.add_argument('-a', '--attributes',
                        help='comma-separated list of ' +
                             'Crossref item attributes to keep',
                        type=str)
    parser.add_argument('-n', '--nulldoi',
                        help='set target ground truth DOIs to null',
                        action='store_true')
    parser.add_argument('-s', '--sample', help='input sample file',
                        type=str, required=True)
    parser.add_argument('-o', '--output', help='output dataset file',
                        type=str, required=True)
    args = parser.parse_args()

    init_logging(args.verbose)

    attributes = []
    if args.attributes is not None:
        attributes = args.attributes.split(',')

    sample_data = read_sample_data(args.sample)
    sample_ref_strings = generate_dataset(sample_data.get(dfk.SAMPLE_SAMPLE),
                                          args.styles.split(','),
                                          attributes)

    if args.nulldoi:
        for ref in sample_ref_strings:
            ref[dfk.DATASET_TARGET_GT][dfk.CR_ITEM_DOI] = None

    if args.distort:
        for ref in sample_ref_strings:
            ref[dfk.DATASET_STYLE] = ref.get(dfk.DATASET_STYLE, '') + '-noise'
            ref[dfk.DATASET_REF_STRING] = \
                add_noise(ref.get(dfk.DATASET_REF_STRING, ''))

    dataset = {dfk.DATASET_DOIS: sample_data.get(dfk.SAMPLE_DOIS),
               dfk.DATASET_DATASET: sample_ref_strings}

    save_dataset(dataset, args.output)
