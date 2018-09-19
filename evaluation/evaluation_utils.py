import utils.data_format_keys as dfk

from dataset.dataset_utils import get_target_gt_doi, get_target_test_doi
from statistics import mean
from utils.utils import safe_div


class ReferenceMetricsResults:

    def __init__(self, dataset):
        self.total = len(dataset)

        self.counts = {}

        self.counts[dfk.EVAL_R_CORRECT_LINK] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) == get_target_test_doi(d)
                 and get_target_gt_doi(d) is not None])
        self.counts[dfk.EVAL_R_CORRECT_NO_LINK] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) == get_target_test_doi(d)
                 and get_target_gt_doi(d) is None])
        self.counts[dfk.EVAL_R_INCORRECT_LINK] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) != get_target_test_doi(d)
                 and get_target_gt_doi(d) is not None
                 and get_target_test_doi(d) is not None])
        self.counts[dfk.EVAL_R_INCORRECT_EXISTS] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) != get_target_test_doi(d)
                 and get_target_gt_doi(d) is None])
        self.counts[dfk.EVAL_R_INCORRECT_MISSING] = \
            len([d for d in dataset
                 if get_target_gt_doi(d) != get_target_test_doi(d)
                 and get_target_test_doi(d) is None])

    def get_count(self, metric):
        return self.counts[metric]

    def get(self, metric):
        if metric == dfk.EVAL_R_ACCURACY:
            return (self.get_count(dfk.EVAL_R_CORRECT_LINK) +
                    self.get_count(dfk.EVAL_R_CORRECT_NO_LINK)) / self.total
        return self.counts[metric] / self.total

    def print_summary(self):
        print('Reference-based metrics:')
        print('  Accuracy: {:.4f}'.format(self.get(dfk.EVAL_R_ACCURACY)))
        print('  Fractions of references:')
        for metric in [dfk.EVAL_R_CORRECT_LINK, dfk.EVAL_R_CORRECT_NO_LINK,
                       dfk.EVAL_R_INCORRECT_LINK, dfk.EVAL_R_INCORRECT_EXISTS,
                       dfk.EVAL_R_INCORRECT_MISSING]:
            print('    - {}: {:.4f} ({})'.format(metric,
                                                 self.get(metric),
                                                 self.get_count(metric)))


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

        self.results[dfk.EVAL_L_PRECISION] = \
            safe_div(correct_count, test_count, 1.)

        self.results[dfk.EVAL_L_RECALL] = \
            safe_div(correct_count, gt_count, 1.)

        self.results[dfk.EVAL_L_F1] = \
            safe_div(2 * self.results[dfk.EVAL_L_PRECISION] *
                     self.results[dfk.EVAL_L_RECALL],
                     self.results[dfk.EVAL_L_PRECISION] +
                     self.results[dfk.EVAL_L_RECALL], 0.)

        self.results_by_doc = {}
        if split_by_doc:
            dataset_by_doc = split_by_doc_attr(dataset)
            self.results_by_doc = {doc: LinkMetricsResults(d, False)
                                   for doc, d in dataset_by_doc.items()}

    def get(self, metric):
        return self.results[metric]

    def get_by_doc(self, metric):
        return {doc: r.get(metric) for doc, r in self.results_by_doc.items()}

    def get_average_by_doc(self, metric):
        return mean(self.get_by_doc(metric).values())

    def print_summary(self):
        print('Link-based metrics:')
        for metric in [dfk.EVAL_L_PRECISION, dfk.EVAL_L_RECALL, dfk.EVAL_L_F1]:
            print('  {}: {:.4f}'.format(metric, self.get(metric)))
        if self.results_by_doc:
            print('Document-level metrics:')
            for metric in [dfk.EVAL_L_PRECISION, dfk.EVAL_L_RECALL,
                           dfk.EVAL_L_F1]:
                print('  Average {}: {:.4f}'
                      .format(metric, self.get_average_by_doc(metric)))


class Results:

    def __init__(self, dataset):
        self.size = len(dataset)
        self.reference_metrics_results = ReferenceMetricsResults(dataset)
        self.link_metrics_results = LinkMetricsResults(dataset)

    def print_summary(self):
        print('Size: {}'.format(self.size))
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
