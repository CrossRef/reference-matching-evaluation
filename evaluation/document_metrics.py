import pandas as pd
import utils.data_format_keys as dfk

from dataset.dataset_utils import get_target_gt_doi, get_target_test_doi
from evaluation.evaluation_utils import doi_gt_same, doi_normalize, \
    doi_test_same, confidence_interval
from statistics import mean
from utils.utils import safe_div


class TargetDocLinkMetricsResults:

    def __init__(self, dataset, target_doi):
        self.target_doi = target_doi

        correct_count = \
            len([d for d in dataset if doi_gt_same(d, target_doi)
                 and doi_test_same(d, target_doi)])
        gt_count = len([d for d in dataset if doi_gt_same(d, target_doi)])
        test_count = len([d for d in dataset if doi_test_same(d, target_doi)])
        self.results = {}
        self.results[dfk.EVAL_PREC] = \
            safe_div(correct_count, test_count, 1.)

        self.results[dfk.EVAL_REC] = \
            safe_div(correct_count, gt_count, 1.)

        self.results[dfk.EVAL_F1] = \
            safe_div(2 * self.results.get(dfk.EVAL_PREC) *
                     self.results.get(dfk.EVAL_REC),
                     self.results.get(dfk.EVAL_PREC) +
                     self.results.get(dfk.EVAL_REC), 0.)

    def get_supported_metrics(self):
        return [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1]

    def get(self, metric):
        return self.results[metric]

    def print_summary(self):
        print('Link-based metrics for target document {}:'
              .format(self.target_doi))
        for metric in self.get_supported_metrics():
            print('  {}: {:.4f}'.format(metric, self.get(metric)))


class ByDocumentMetricsResults:

    def __init__(self, dataset, target_dois):
        self.metrics = \
            [dfk.EVAL_MEAN_PREC, dfk.EVAL_MEAN_REC, dfk.EVAL_MEAN_F1,
             dfk.EVAL_CI_PREC, dfk.EVAL_CI_REC, dfk.EVAL_CI_F1,
             dfk.EVAL_DOC_METRICS]

        self.metrics_groups = \
            [(dfk.EVAL_MEAN_PREC, dfk.EVAL_CI_PREC, dfk.EVAL_PREC),
             (dfk.EVAL_MEAN_REC, dfk.EVAL_CI_REC, dfk.EVAL_REC),
             (dfk.EVAL_MEAN_F1, dfk.EVAL_CI_F1, dfk.EVAL_F1)]

        target_dois_norm = [doi_normalize(doi) for doi in target_dois]
        dataset_split = {doi: [] for doi in target_dois_norm}
        for d in dataset:
            doi_gt = doi_normalize(get_target_gt_doi(d))
            if doi_gt in target_dois_norm:
                dataset_split[doi_gt].append(d)
            doi_test = doi_normalize(get_target_test_doi(d))
            if doi_test != doi_gt and  doi_test in target_dois_norm:
                dataset_split[doi_test].append(d)

        results_by_doc = \
            [(doi,
              TargetDocLinkMetricsResults(dataset_split[doi_normalize(doi)],
                                          doi))
             for doi in target_dois]

        self.results = {}

        for av, ci, m in self.metrics_groups:
            if results_by_doc:
                self.results[av] = mean([r.get(m) for _, r in results_by_doc])
                self.results[ci] = \
                    confidence_interval([r.get(m) for _, r in results_by_doc],
                                        .95)
            else:
                self.results[ci] = None
                self.results[av] = None

        doc_metrics = {'doc': [d for d, _ in results_by_doc]}
        for metric in [dfk.EVAL_PREC, dfk.EVAL_REC, dfk.EVAL_F1]:
            doc_metrics[metric] = [r.get(metric) for _, r in results_by_doc]
        self.results[dfk.EVAL_DOC_METRICS] = pd.DataFrame(doc_metrics)

    def get_supported_metrics(self):
        return self.metrics

    def get(self, metric):
        return self.results.get(metric)

    def print_summary(self):
        print('Link-based metrics by target documents:')
        for av, ci, m in self.metrics_groups:
            print('  Average {}: {:.4f} (CI: {})'
                  .format(m, self.get(av), self.get(ci)))
