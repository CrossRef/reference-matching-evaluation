import argparse
import utils.data_format_keys as dfk

from evaluation.evaluation_utils import Results
from utils.utils import init_logging, read_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='evaluate citation matcher')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-d', '--dataset', required=True, type=str)
    parser.add_argument('-s', '--splitattr', type=str)
    parser.add_argument('-o', '--outputdoc', type=str)

    args = parser.parse_args()

    init_logging(args.verbose)

    dataset = read_json(args.dataset)

    results = Results(dataset)
    results.print_summary()

    if args.outputdoc:
        results.get(dfk.EVAL_DOC_METRICS).to_csv(args.outputdoc, index=False)
