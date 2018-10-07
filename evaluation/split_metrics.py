import pandas as pd
import utils.data_format_keys as dfk

from evaluation.document_metrics import ByDocumentMetricsResults
from evaluation.link_metrics import LinkMetricsResults
from evaluation.reference_metrics import ReferenceMetricsResults
from evaluation.evaluation_utils import doi_equals, doi_gt_null, \
    doi_test_null, split_by_ref_attr
from utils.utils import safe_div


class DocAttrLinkMetricsResults:

    def __init__(self, dataset, attr, value):
        self.attr = attr
        self.value = value

        correct_count = \
            len([d for d in dataset if doi_equals(d) and not doi_gt_null(d)
                 and d[dfk.DATASET_TARGET_GT][attr] == value])
        gt_count = len([d for d in dataset if not doi_gt_null(d)
                        and d[dfk.DATASET_TARGET_GT][attr] == value])
        test_count = len([d for d in dataset if not doi_test_null(d)
                          and d[dfk.DATASET_TARGET_TEST][attr] == value])
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

    def get_supported_metrics(self):
        return [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1]

    def get(self, metric):
        return self.results[metric]

    def print_summary(self):
        print('Link-based metrics for {} = {}:'
              .format(self.attr, self.value))
        for metric in self.get_supported_metrics():
            print('  {}: {:.4f}'.format(metric, self.get(metric)))


class SplitByDocAttrResults:

    def __init__(self, dataset, attr):
        self.attr = attr

        values = list(set(
            [d.get(dfk.DATASET_TARGET_GT).get(attr) for d in dataset] +
            [d.get(dfk.DATASET_TARGET_TEST).get(attr) for d in dataset]))
        self.split_results = {a: DocAttrLinkMetricsResults(dataset, attr, a)
                              for a in values}

        metrics = {self.attr: values}
        for metric in [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1]:
            metrics[metric] = [self.split_results[a].get(metric)
                               for a in metrics[self.attr]]

        self.results = {}
        self.results[dfk.EVAL_SPLIT_METRICS] = pd.DataFrame(metrics)

    def get_supported_metrics(self):
        return [dfk.EVAL_SPLIT_METRICS]

    def get(self, metric):
        return self.results[metric]

    def print_summary(self):
        for value in self.split_results.keys():
            print()
            print('{}: {}'.format(self.attr, value))
            self.split_results[value].print_summary()


class SplitByRefAttrResults:

    def __init__(self, dataset, attr, target_dois):
        self.attr = attr
        split_dataset = split_by_ref_attr(dataset, attr)

        self.ref_split_results = {a: ReferenceMetricsResults(s)
                                  for a, s in split_dataset.items()}
        self.doc_split_results = {a: ByDocumentMetricsResults(s, target_dois)
                                  for a, s in split_dataset.items()}
        self.link_split_results = {a: LinkMetricsResults(s)
                                   for a, s in split_dataset.items()}

        attr_metrics = {self.attr: list(split_dataset.keys())}
        for metric in [dfk.EVAL_CORR_LINK_F, dfk.EVAL_CORR_NO_LINK_F,
                       dfk.EVAL_INCORR_LINK_F, dfk.EVAL_INCORR_EXISTS_F,
                       dfk.EVAL_INCORR_MISSING_F, dfk.EVAL_ACCURACY]:
            attr_metrics[metric] = [self.ref_split_results[a].get(metric)
                                    for a in attr_metrics[self.attr]]

        for metric in [dfk.EVAL_MEAN_PREC, dfk.EVAL_MEAN_REC,
                       dfk.EVAL_MEAN_F1]:
            attr_metrics[metric] = [self.doc_split_results[a].get(metric)
                                    for a in attr_metrics[self.attr]]

        for metric in [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1]:
            attr_metrics[metric] = [self.link_split_results[a].get(metric)
                                    for a in attr_metrics[self.attr]]

        self.results = {}
        self.results[dfk.EVAL_SPLIT_METRICS] = pd.DataFrame(attr_metrics)

    def get_supported_metrics(self):
        return [dfk.EVAL_SPLIT_METRICS]

    def get(self, metric):
        return self.results[metric]

    def print_summary(self):
        for value in self.ref_split_results.keys():
            print()
            print('{}: {}'.format(self.attr, value))
            self.ref_split_results[value].print_summary()
            self.link_split_results[value].print_summary()
            self.doc_split_results[value].print_summary()
