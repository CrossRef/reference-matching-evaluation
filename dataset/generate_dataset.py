import argparse
import itertools
import logging
import utils.data_format_keys as dfk

from dataset.draw_sample import read_sample_data
from utils.cr_utils import create_ref_string
from utils.utils import init_logging, read_json, save_json


def save_dataset(ref_strings, file_path):
    save_json(ref_strings, file_path)
    logging.info('Dataset written to {}'.format(file_path))


def read_dataset(file_path):
    return read_json(file_path)


def keep_fields(doc, fields):
    return {k: f for k, f in doc.items()
            if k == dfk.CR_ITEM_DOI or k in fields}


def generate_dataset(sample, styles, fields):
    logging.info('Generating dataset')
    prod_sample_style = itertools.product(sample, styles)
    prod_sample_style = [(i, p[0], p[1])
                         for i, p in enumerate(prod_sample_style)]
    results = [{dfk.DATASET_REF_ID: i+1,
                dfk.DATASET_STYLE: s,
                dfk.DATASET_REF_STRING:
                    create_ref_string(d[dfk.CR_ITEM_DOI], s),
                dfk.DATASET_TARGET_GT: keep_fields(d, fields)}
               for i, d, s in prod_sample_style]

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='create a simple evaluation dataset')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-l', '--styles',
                        help='comma-separated list of citationstyle names',
                        type=str, default='apa')
    parser.add_argument('-s', '--sample', help='input sample file',
                        type=str, required=True)
    parser.add_argument('-o', '--output', help='output dataset file',
                        type=str, required=True)
    args = parser.parse_args()

    init_logging(args.verbose)

    sample_data = read_sample_data(args.sample)
    sample_ref_strings = generate_dataset(sample_data[dfk.SAMPLE_SAMPLE],
                                          args.styles.split(','),
                                          [])
    save_dataset(sample_ref_strings, args.output)
