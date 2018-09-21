import argparse
import logging
import utils.data_format_keys as dfk

from utils.cr_utils import get_sample, parse_filter_text
from utils.utils import init_logging, read_json, save_json, timestamp


def generate_sample_data(size, filter, query):
    logging.info('Getting a sample of items')
    sample = get_sample(size, filter, query)
    return {dfk.SAMPLE_TIMESTAMP: timestamp(),
            dfk.SAMPLE_FILTER: filter,
            dfk.SAMPLE_QUERY: query,
            dfk.SAMPLE_SIZE: size,
            dfk.SAMPLE_DOIS: [s[dfk.CR_ITEM_DOI] for s in sample],
            dfk.SAMPLE_SAMPLE: sample}


def save_sample_data(sample_data, file_path):
    save_json(sample_data, file_path)
    logging.info('Sample data written to {}'.format(file_path))


def read_sample_data(file_path):
    return read_json(file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Draw a sample of items')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-s', '--size', help='size of sample', type=int,
                        required=True)
    parser.add_argument('-f', '--filter', help='filter', type=str,
                        default='')
    parser.add_argument('-q', '--query', help='query', type=str, default='')
    parser.add_argument('-o', '--output', help='output file',
                        type=str, required=True)
    args = parser.parse_args()

    init_logging(args.verbose)

    if args.filter:
        args.filter = parse_filter_text(args.filter)
    else:
        args.filter = {}

    sample_data = generate_sample_data(args.size, args.filter, args.query)
    save_sample_data(sample_data, args.output)
