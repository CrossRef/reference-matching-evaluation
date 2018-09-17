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
    print('Raw results: {}'.format(ref_metrics_results.results))
    print('Accuracy: {}'.format(ref_metrics_results.get_accuracy()))

#   link-baised metrics
    link_metrics_results = LinkMetricsResults(dataset)
    print('Precision: {}'.format(link_metrics_results.get_precision()))
    print('Recall: {}'.format(link_metrics_results.get_recall()))
    print('F1: {}'.format(link_metrics_results.get_f1()))
