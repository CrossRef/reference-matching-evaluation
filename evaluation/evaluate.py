import argparse

from evaluation.evaluation_utils import LinkMetricsResults, \
    ReferenceMetricsResults
from utils.utils import init_logging, read_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='evaluate citation matcher')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-d', '--dataset', required=True, type=str)

    args = parser.parse_args()

    init_logging(args.verbose)

    dataset = read_json(args.dataset)

#   reference-based metrics
    ref_metrics_results = ReferenceMetricsResults(dataset)
    ref_metrics_results.print_summary()

#   link-based metrics
    link_metrics_results = LinkMetricsResults(dataset)
    link_metrics_results.print_summary()
