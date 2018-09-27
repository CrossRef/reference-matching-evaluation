import os
import utils.data_format_keys as dfk

from evaluation.document_metrics import ByDocumentMetricsResults, \
    TargetDocLinkMetricsResults
from pytest import approx, fixture
from utils.utils import read_json


SINGLE_CORRECT = \
    [{'style': 'ieee',
      'ref_string': 'A very smart and influential paper.',
      'target_gt': {
        'DOI': '10.14195/2182-7087_2_1d',
        'type': 'journal-article'
      },
      'target_test': {
        'DOI': '10.14195/2182-7087_2_1D',
        'type': 'journal-article'
      }}]

SINGLE_INCORRECT = \
    [{'style': 'ieee',
      'ref_string': 'A very smart and influential paper.',
      'target_gt': {
        'DOI': '10.14195/2182-7087_2_1',
        'type': 'journal-article'
      },
      'target_test': {
        'DOI': '10.14195/2182-708',
        'type': 'journal-article'
      }}]


@fixture
def datadir(request):
    filename = request.module.__file__
    test_dir, _ = os.path.split(filename)
    return test_dir + '/'


class TestTargetDocLinkMetrics:

    def test_absent(self):
        r = TargetDocLinkMetricsResults(SINGLE_CORRECT, 'absent_doi')
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(1)

    def test_single_correct(self):
        r = TargetDocLinkMetricsResults(SINGLE_CORRECT,
                                        '10.14195/2182-7087_2_1d')
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(1)

    def test_single_incorrect(self):
        r = TargetDocLinkMetricsResults(SINGLE_INCORRECT,
                                        '10.14195/2182-7087_2_1')
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(0)
        assert r.get(dfk.EVAL_F1) == approx(0)

        r = TargetDocLinkMetricsResults(SINGLE_INCORRECT,
                                        '10.14195/2182-708')
        assert r.get(dfk.EVAL_PREC) == approx(0)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(0)

    def test_full(self, datadir):
        data = read_json(datadir + 'test_dataset.json')['dataset']
        r = TargetDocLinkMetricsResults(data, '10.1103/physrevb.67.134406')
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(1)

        r = TargetDocLinkMetricsResults(data, '10.1159/000408205')
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(1/2)
        assert r.get(dfk.EVAL_F1) == approx(2/3)

        r = TargetDocLinkMetricsResults(data, '10.1002/chin.199827068')
        assert r.get(dfk.EVAL_PREC) == approx(1/3)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(1/2)


class TestByDocumentMetrics:

    def test_absent(self):
        r = ByDocumentMetricsResults(SINGLE_CORRECT, ['absent_doi'])
        assert r.get(dfk.EVAL_MEAN_PREC) == approx(1)
        assert r.get(dfk.EVAL_MEAN_REC) == approx(1)
        assert r.get(dfk.EVAL_MEAN_F1) == approx(1)

    def test_single_correct(self):
        r = ByDocumentMetricsResults(SINGLE_CORRECT,
                                     ['10.14195/2182-7087_2_1D'])
        assert r.get(dfk.EVAL_MEAN_PREC) == approx(1)
        assert r.get(dfk.EVAL_MEAN_REC) == approx(1)
        assert r.get(dfk.EVAL_MEAN_F1) == approx(1)

    def test_single_incorrect(self):
        r = ByDocumentMetricsResults(SINGLE_INCORRECT,
                                     ['10.14195/2182-7087_2_1',
                                      '10.14195/2182-708'])
        assert r.get(dfk.EVAL_MEAN_PREC) == approx(1/2)
        assert r.get(dfk.EVAL_MEAN_REC) == approx(1/2)
        assert r.get(dfk.EVAL_MEAN_F1) == approx(0)

    def test_full(self, datadir):
        data = read_json(datadir + 'test_dataset.json')['dataset']
        r = ByDocumentMetricsResults(data, ['10.1103/physrevb.67.134406',
                                            '10.1159/000408205',
                                            '10.1002/chin.199827068'])
        assert r.get(dfk.EVAL_MEAN_PREC) == approx(7/9)
        assert r.get(dfk.EVAL_MEAN_REC) == approx(5/6)
        assert r.get(dfk.EVAL_MEAN_F1) == approx(13/18)

    def test_full_summary(self, datadir):
        data = read_json(datadir + 'test_dataset.json')
        r = ByDocumentMetricsResults(data['dataset'], data['dataset_dois'])
        doc_r = r.get(dfk.EVAL_DOC_METRICS)
        doc_r = doc_r.sort_values(by='doc')
        assert doc_r.shape == (10, 4)
        assert doc_r['doc'].tolist() == sorted(data['dataset_dois'])
        assert doc_r['precision'].tolist()[0] == approx(1/3)
        assert doc_r['precision'].tolist()[9] == approx(1)
        assert doc_r['recall'].tolist()[0] == approx(1)
        assert doc_r['recall'].tolist()[9] == approx(0)
        assert doc_r['F1'].tolist()[0] == approx(1/2)
        assert doc_r['F1'].tolist()[9] == approx(0)
