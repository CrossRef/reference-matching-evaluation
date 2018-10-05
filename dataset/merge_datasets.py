import argparse
import utils.data_format_keys as dfk

from dataset.generate_dataset import read_dataset, save_dataset
from utils.utils import init_logging, timestamp


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='merge two or more datasets')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-d', '--datasets',
                        help='comma-separated list of paths',
                        type=str, required=True)
    parser.add_argument('-o', '--output', help='output dataset file',
                        type=str, required=True)
    args = parser.parse_args()

    init_logging(args.verbose)

    paths = args.datasets.split(',')
    data = read_dataset(paths[0])

    if dfk.SAMPLE_SAMPLE in data:
        all_dois = []
        all_data = []
        size = 0
        for path in paths:
            data = read_dataset(path)
            filter = data[dfk.SAMPLE_FILTER]
            query = data[dfk.SAMPLE_QUERY]
            size = size + data[dfk.SAMPLE_SIZE]
            all_dois.extend(data[dfk.SAMPLE_DOIS])
            all_data.extend(data[dfk.SAMPLE_SAMPLE])
        dataset = {dfk.SAMPLE_TIMESTAMP: timestamp(),
                   dfk.SAMPLE_FILTER: filter,
                   dfk.SAMPLE_QUERY: query,
                   dfk.SAMPLE_SIZE: size,
                   dfk.SAMPLE_DOIS: list(set(all_dois)),
                   dfk.SAMPLE_SAMPLE: all_data}
    else:
        all_dois = []
        all_data = []
        for path in paths:
            data = read_dataset(path)
            all_dois.extend(data[dfk.DATASET_DOIS])
            all_data.extend(data[dfk.DATASET_DATASET])
        dataset = {dfk.DATASET_DOIS: list(set(all_dois)),
                   dfk.DATASET_DATASET: all_data}

    save_dataset(dataset, args.output)
