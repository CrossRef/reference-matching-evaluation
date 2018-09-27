import utils.data_format_keys as dfk

from evaluation.evaluation_utils import doi_equals, doi_gt_null, doi_test_null
from utils.utils import safe_div


class LinkMetricsResults:

    def __init__(self, dataset):
        self.metrics = [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1]

        correct_count = \
            len([d for d in dataset if doi_equals(d) and not doi_gt_null(d)])
        gt_count = len([d for d in dataset if not doi_gt_null(d)])
        test_count = len([d for d in dataset if not doi_test_null(d)])

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
        return self.metrics

    def get(self, metric):
        return self.results[metric]

    def print_summary(self):
        print('Link-based metrics:')
        for metric in self.metrics:
            print('  {}: {:.4f}'.format(metric, self.get(metric)))
