import argparse
import logging
import utils.data_format_keys as dfk

from dataset.draw_sample import read_sample_data
from utils.cr_utils import create_ref_string
from utils.utils import init_logging, read_json, save_json


def generate_ref_strings(sample, styles):
    logging.info('Generating reference strings')
    results = [{dfk.DATASET_DOI_GT: item[dfk.CR_ITEM_DOI],
                dfk.DATASET_STYLE: style,
                dfk.DATASET_REF_STRING:
                    create_ref_string(item[dfk.CR_ITEM_DOI], style)}
               for item in sample for style in styles]
    [r.update({dfk.DATASET_REF_ID: i+1}) for i, r in enumerate(results)]
    return results


def save_ref_strings(ref_strings, file_path):
    save_json(ref_strings, file_path)
    logging.info('Reference strings written to {}'.format(file_path))


def read_ref_strings(file_path):
    return read_json(file_path)


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
    sample_ref_strings = generate_ref_strings(sample_data[dfk.SAMPLE_SAMPLE],
                                              args.styles.split(','))
    save_ref_strings(sample_ref_strings, args.output)
