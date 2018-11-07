import utils.data_format_keys as dfk

from evaluation.evaluation_utils import confidence_interval_prop, doi_equals, \
    doi_gt_null, doi_test_null
from utils.utils import safe_div


class LinkMetricsResults:

    def __init__(self, dataset):
        self.metrics = [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1,
                        dfk.EVAL_CI_PREC, dfk.EVAL_CI_REC]

        correct_count = \
            len([d for d in dataset if doi_equals(d) and not doi_gt_null(d)])
        gt_count = len([d for d in dataset if not doi_gt_null(d)])
        test_count = len([d for d in dataset if not doi_test_null(d)])

        self.results = {}

        self.results[dfk.EVAL_PREC] = \
            safe_div(correct_count, test_count, 1.)

        self.results[dfk.EVAL_CI_PREC] = \
            confidence_interval_prop(correct_count, test_count, 0.95)

        self.results[dfk.EVAL_REC] = \
            safe_div(correct_count, gt_count, 1.)

        self.results[dfk.EVAL_CI_REC] = \
            confidence_interval_prop(correct_count, gt_count, 0.95)

        self.results[dfk.EVAL_F1] = \
            safe_div(2 * self.results.get(dfk.EVAL_PREC) *
                     self.results.get(dfk.EVAL_REC),
                     self.results.get(dfk.EVAL_PREC) +
                     self.results.get(dfk.EVAL_REC), 0.)

    def get_supported_metrics(self):
        return self.metrics

    def get(self, metric):
        return self.results.get(metric)

    def print_summary(self):
        print('Link-based metrics:')
        print('  Precision: {:.4f} (CI: {})'
              .format(self.get(dfk.EVAL_PREC), self.get(dfk.EVAL_CI_PREC)))
        print('  Recall: {:.4f} (CI: {})'
              .format(self.get(dfk.EVAL_REC), self.get(dfk.EVAL_CI_REC)))
        print('  F1: {:.4f}'.format(self.get(dfk.EVAL_F1)))
