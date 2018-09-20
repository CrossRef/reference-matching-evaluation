import pandas as pd
import utils.data_format_keys as dfk

from dataset.dataset_utils import get_target_gt_doi, get_target_test_doi
from statistics import mean
from utils.utils import safe_div


REFERENCE_METRICS = \
    [dfk.EVAL_REF_TOTAL, dfk.EVAL_CORR_LINK_C, dfk.EVAL_CORR_NO_LINK_C,
     dfk.EVAL_INCORR_LINK_C, dfk.EVAL_INCORR_EXISTS_C,
     dfk.EVAL_INCORR_MISSING_C, dfk.EVAL_CORR_LINK_F, dfk.EVAL_CORR_NO_LINK_F,
     dfk.EVAL_INCORR_LINK_F, dfk.EVAL_INCORR_EXISTS_F,
     dfk.EVAL_INCORR_MISSING_F, dfk.EVAL_ACCURACY]

REFERENCE_METRICS_PAIRS = \
    [(dfk.EVAL_CORR_LINK_C, dfk.EVAL_CORR_LINK_F),
     (dfk.EVAL_CORR_NO_LINK_C, dfk.EVAL_CORR_NO_LINK_F),
     (dfk.EVAL_INCORR_LINK_C, dfk.EVAL_INCORR_LINK_F),
     (dfk.EVAL_INCORR_EXISTS_C, dfk.EVAL_INCORR_EXISTS_F),
     (dfk.EVAL_INCORR_MISSING_C, dfk.EVAL_INCORR_MISSING_F)]

LINK_METRICS = [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1, dfk.EVAL_MEAN_PREC,
                dfk.EVAL_MEAN_REC, dfk.EVAL_MEAN_F1, dfk.EVAL_DOC_METRICS]

LINK_METRICS_PAIRS = [(dfk.EVAL_MEAN_PREC, dfk.EVAL_PREC),
                      (dfk.EVAL_MEAN_REC, dfk.EVAL_REC),
                      (dfk.EVAL_MEAN_F1, dfk.EVAL_F1)]


class ReferenceMetricsResults:

    def __init__(self, dataset):
        self.results = {}

        self.results[dfk.EVAL_REF_TOTAL] = len(dataset)

        self.results[dfk.EVAL_CORR_LINK_C] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) == get_target_test_doi(d)
                 and get_target_gt_doi(d) is not None])
        self.results[dfk.EVAL_CORR_NO_LINK_C] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) == get_target_test_doi(d)
                 and get_target_gt_doi(d) is None])
        self.results[dfk.EVAL_INCORR_LINK_C] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) != get_target_test_doi(d)
                 and get_target_gt_doi(d) is not None
                 and get_target_test_doi(d) is not None])
        self.results[dfk.EVAL_INCORR_EXISTS_C] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) != get_target_test_doi(d)
                 and get_target_gt_doi(d) is None])
        self.results[dfk.EVAL_INCORR_MISSING_C] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) != get_target_test_doi(d)
                 and get_target_test_doi(d) is None])

        for count, fraction in REFERENCE_METRICS_PAIRS:
            self.results[fraction] = \
                self.results[count] / self.results[dfk.EVAL_REF_TOTAL]

        self.results[dfk.EVAL_ACCURACY] = \
            (self.results[dfk.EVAL_CORR_LINK_C] +
             self.results[dfk.EVAL_CORR_NO_LINK_C]) / \
            self.results[dfk.EVAL_REF_TOTAL]

    def get_supported_metrics(self):
        return REFERENCE_METRICS

    def get(self, metric):
        return self.results[metric]

    def print_summary(self):
        print('Reference-based metrics:')
        print('  Number of references: {}'
              .format(self.get(dfk.EVAL_REF_TOTAL)))
        print('  Accuracy: {:.4f}'.format(self.get(dfk.EVAL_ACCURACY)))
        print('  Fractions of references:')
        for count, fraction in REFERENCE_METRICS_PAIRS:
            print('    - {}: {:.4f} ({})'.format(fraction,
                                                 self.get(fraction),
                                                 self.get(count)))


class LinkMetricsResults:

    def __init__(self, dataset, split_by_doc=True):
        correct_count = len([d for d in dataset
                             if get_target_gt_doi(d) == get_target_test_doi(d)
                             and get_target_gt_doi(d) is not None])
        gt_count = len([d for d in dataset
                        if get_target_gt_doi(d) is not None])
        test_count = len([d for d in dataset
                          if get_target_test_doi(d) is not None])

        self.results = {}

        self.results[dfk.EVAL_PREC] = \
            safe_div(correct_count, test_count, 1.)

        self.results[dfk.EVAL_REC] = \
            safe_div(correct_count, gt_count, 1.)

        self.results[dfk.EVAL_F1] = \
            safe_div(2 * self.results[dfk.EVAL_PREC] *
                     self.results[dfk.EVAL_REC],
                     self.results[dfk.EVAL_PREC] +
                     self.results[dfk.EVAL_REC], 0.)

        results_by_doc = {}
        if split_by_doc:
            dataset_by_doc = split_by_doc_attr(dataset)
            results_by_doc = [(doc, LinkMetricsResults(d, False))
                              for doc, d in dataset_by_doc.items()]

        for av, metric in LINK_METRICS_PAIRS:
            if results_by_doc:
                self.results[av] = \
                    mean([r.get(metric) for _, r in results_by_doc])
            else:
                self.results[av] = None

        doc_metrics = {'doc': [d for d, _ in results_by_doc]}
        for metric in [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1]:
            doc_metrics.update(
                {metric: [r.get(metric) for _, r in results_by_doc]})
        self.results[dfk.EVAL_DOC_METRICS] = pd.DataFrame(doc_metrics)

    def get_supported_metrics(self):
        return [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1,
                dfk.EVAL_MEAN_PREC, dfk.EVAL_MEAN_REC, dfk.EVAL_MEAN_F1]

    def get(self, metric):
        return self.results[metric]

    def print_summary(self):
        print('Link-based metrics:')
        for metric in [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1]:
            print('  {}: {:.4f}'.format(metric, self.get(metric)))
        print('Document-level metrics:')
        for metric in [dfk.EVAL_MEAN_PREC, dfk.EVAL_MEAN_REC,
                       dfk.EVAL_MEAN_F1]:
            print('  Average {}: {:.4f}'.format(metric, self.get(metric)))


class Results:

    def __init__(self, dataset):
        self.reference_metrics_results = ReferenceMetricsResults(dataset)
        self.link_metrics_results = LinkMetricsResults(dataset)

    def get_supported_metrics(self):
        return self.reference_metrics_results.get_supported_metrics() + \
               self.link_metrics_results.get_supported_metrics()

    def get(self, metric):
        if metric in self.reference_metrics_results.get_supported_metrics():
            return self.reference_metrics_results.get(metric)
        return self.link_metrics_results.get(metric)

    def print_summary(self):
        self.reference_metrics_results.print_summary()
        self.link_metrics_results.print_summary()


class SplitResults:

    def __init__(self, dataset, attr):
        self.attr = attr
        if attr in dataset[0]:
            self.split_dataset = split_by_ref_attr(dataset, attr)
        else:
            self.split_dataset = split_by_doc_attr(dataset, attr)
        self.split_results = {a: Results(s)
                              for a, s in self.split_dataset.items()}

    def get_supported_metrics(self):
        return [dfk.EVAL_SPLIT_METRICS, dfk.EVAL_SPLIT_DOC_METRICS]

    def get(self, metric):
        # TODO
        return None

    def print_summary(self):
        for value, dataset in self.split_dataset.items():
            print()
            print('{}: {}'.format(self.attr, value))
            self.split_results[value].print_summary()


def split_by_ref_attr(dataset, attr):
    split_values = set([d[attr] for d in dataset if d[attr] is not None])
    split_dataset = {v: [] for v in split_values}
    for item in dataset:
        if item[attr] is not None:
            split_dataset[item[attr]].append(item)
    return split_dataset


def split_by_doc_attr(dataset, attr=dfk.CR_ITEM_DOI):
    split_values = set([d[dfk.DATASET_TARGET_GT][attr]
                        for d in dataset
                        if d[dfk.DATASET_TARGET_GT][attr] is not None])
    split_dataset = {v: [] for v in split_values}
    for item in dataset:
        item_target = item[dfk.DATASET_TARGET_GT]
        if attr in item_target:
            gt_attr = item[dfk.DATASET_TARGET_GT][attr]
            if gt_attr is not None:
                split_dataset[gt_attr].append(item)
        item_test = item[dfk.DATASET_TARGET_TEST]
        if attr in item_test:
            test_attr = item[dfk.DATASET_TARGET_TEST][attr]
            if test_attr in split_dataset:
                if item not in split_dataset[test_attr]:
                    split_dataset[test_attr].append(item)
    return split_dataset
