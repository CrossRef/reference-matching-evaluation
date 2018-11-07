import utils.data_format_keys as dfk

from evaluation.evaluation_utils import confidence_interval_prop, doi_equals, \
    doi_gt_null, doi_test_null


class ReferenceMetricsResults:

    def __init__(self, dataset):
        self.metrics = \
            [dfk.EVAL_REF_TOTAL, dfk.EVAL_CORR_LINK_C,
             dfk.EVAL_CORR_NO_LINK_C, dfk.EVAL_INCORR_LINK_C,
             dfk.EVAL_INCORR_EXISTS_C, dfk.EVAL_INCORR_MISSING_C,
             dfk.EVAL_CORR_LINK_F, dfk.EVAL_CORR_NO_LINK_F,
             dfk.EVAL_INCORR_LINK_F, dfk.EVAL_INCORR_EXISTS_F,
             dfk.EVAL_INCORR_MISSING_F, dfk.EVAL_ACCURACY,
             dfk.EVAL_CI_ACCURACY]
        self.metrics_groups = \
            [(dfk.EVAL_CORR_LINK_C, dfk.EVAL_CORR_LINK_F),
             (dfk.EVAL_CORR_NO_LINK_C, dfk.EVAL_CORR_NO_LINK_F),
             (dfk.EVAL_INCORR_LINK_C, dfk.EVAL_INCORR_LINK_F),
             (dfk.EVAL_INCORR_EXISTS_C, dfk.EVAL_INCORR_EXISTS_F),
             (dfk.EVAL_INCORR_MISSING_C, dfk.EVAL_INCORR_MISSING_F)]

        self.results = {}

        self.results[dfk.EVAL_REF_TOTAL] = len(dataset)

        self.results[dfk.EVAL_CORR_LINK_C] = \
            len([d for d in dataset if doi_equals(d) and not doi_gt_null(d)])
        self.results[dfk.EVAL_CORR_NO_LINK_C] = \
            len([d for d in dataset if doi_equals(d) and doi_gt_null(d)])
        self.results[dfk.EVAL_INCORR_LINK_C] = \
            len([d for d in dataset if not doi_equals(d)
                 and not doi_gt_null(d) and not doi_test_null(d)])
        self.results[dfk.EVAL_INCORR_EXISTS_C] = \
            len([d for d in dataset if not doi_equals(d) and doi_gt_null(d)])
        self.results[dfk.EVAL_INCORR_MISSING_C] = \
            len([d for d in dataset if not doi_equals(d) and doi_test_null(d)])

        for count, fraction in self.metrics_groups:
            self.results[fraction] = \
                self.results.get(count) / self.results.get(dfk.EVAL_REF_TOTAL)

        self.results[dfk.EVAL_ACCURACY] = \
            (self.results.get(dfk.EVAL_CORR_LINK_C) +
             self.results.get(dfk.EVAL_CORR_NO_LINK_C)) / \
            self.results.get(dfk.EVAL_REF_TOTAL)

        self.results[dfk.EVAL_CI_ACCURACY] = \
            confidence_interval_prop(self.results.get(dfk.EVAL_CORR_LINK_C) +
                                     self.results.get(dfk.EVAL_CORR_NO_LINK_C),
                                     self.results.get(dfk.EVAL_REF_TOTAL),
                                     0.95)

    def get_supported_metrics(self):
        return self.metrics

    def get(self, metric):
        return self.results.get(metric)

    def print_summary(self):
        print('Reference-based metrics:')
        print('  Number of references: {}'
              .format(self.get(dfk.EVAL_REF_TOTAL)))
        print('  Accuracy: {:.4f} (CI: {})'
              .format(self.get(dfk.EVAL_ACCURACY),
                      self.get(dfk.EVAL_CI_ACCURACY)))
        print('  Fractions of references:')
        for count, fraction in self.metrics_groups:
            print('    - {}: {:.4f} ({})'.format(fraction,
                                                 self.get(fraction),
                                                 self.get(count)))
