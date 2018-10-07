import argparse
import utils.data_format_keys as dfk

from evaluation.document_metrics import ByDocumentMetricsResults
from evaluation.link_metrics import LinkMetricsResults
from evaluation.reference_metrics import ReferenceMetricsResults
from evaluation.split_metrics import SplitByDocAttrResults, \
    SplitByRefAttrResults
from utils.utils import init_logging, read_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='evaluate citation matcher')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-d', '--dataset', help='dataset file', required=True,
                        type=str)
    parser.add_argument('-s', '--splitattr',
                        help='name of the attribute to split the results by',
                        type=str)
    parser.add_argument('-o', '--outputdoc',
                        help='output file for the results by target document',
                        type=str)
    parser.add_argument('-p', '--outputsplit',
                        help='output file for the results by the split ' +
                        'attribute', type=str)

    args = parser.parse_args()

    init_logging(args.verbose)

    dataset = read_json(args.dataset)

    ref_results = ReferenceMetricsResults(dataset.get(dfk.DATASET_DATASET))
    ref_results.print_summary()

    link_results = LinkMetricsResults(dataset.get(dfk.DATASET_DATASET))
    link_results.print_summary()

    doc_results = ByDocumentMetricsResults(dataset.get(dfk.DATASET_DATASET),
                                           dataset.get(dfk.DATASET_DOIS))
    doc_results.print_summary()

    if args.outputdoc:
        doc_results.get(dfk.EVAL_DOC_METRICS).to_csv(args.outputdoc,
                                                     index=False)

    if args.splitattr:
        if args.splitattr in dataset.get(dfk.DATASET_DATASET)[0]:
            split_results = \
                SplitByRefAttrResults(dataset.get(dfk.DATASET_DATASET),
                                      args.splitattr,
                                      dataset.get(dfk.DATASET_DOIS))
        else:
            split_results = \
                SplitByDocAttrResults(dataset.get(dfk.DATASET_DATASET),
                                      args.splitattr)
        split_results.print_summary()
        if args.outputsplit:
            split_results.get(dfk.EVAL_SPLIT_METRICS).to_csv(args.outputsplit,
                                                             index=False)
