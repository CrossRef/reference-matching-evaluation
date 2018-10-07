import os
import utils.data_format_keys as dfk

from evaluation.reference_metrics import ReferenceMetricsResults
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


class TestReferenceMetrics:

    def test_single_correct(self):
        r = ReferenceMetricsResults(SINGLE_CORRECT)
        assert r.get(dfk.EVAL_REF_TOTAL) == approx(1)
        assert r.get(dfk.EVAL_CORR_LINK_C) == approx(1)
        assert r.get(dfk.EVAL_CORR_NO_LINK_C) == approx(0)
        assert r.get(dfk.EVAL_INCORR_LINK_C) == approx(0)
        assert r.get(dfk.EVAL_INCORR_EXISTS_C) == approx(0)
        assert r.get(dfk.EVAL_INCORR_MISSING_C) == approx(0)
        assert r.get(dfk.EVAL_CORR_LINK_F) == approx(1)
        assert r.get(dfk.EVAL_CORR_NO_LINK_F) == approx(0)
        assert r.get(dfk.EVAL_INCORR_LINK_F) == approx(0)
        assert r.get(dfk.EVAL_INCORR_EXISTS_F) == approx(0)
        assert r.get(dfk.EVAL_INCORR_MISSING_F) == approx(0)
        assert r.get(dfk.EVAL_ACCURACY) == approx(1)

    def test_single_incorrect(self):
        r = ReferenceMetricsResults(SINGLE_INCORRECT)
        assert r.get(dfk.EVAL_REF_TOTAL) == approx(1)
        assert r.get(dfk.EVAL_CORR_LINK_C) == approx(0)
        assert r.get(dfk.EVAL_CORR_NO_LINK_C) == approx(0)
        assert r.get(dfk.EVAL_INCORR_LINK_C) == approx(1)
        assert r.get(dfk.EVAL_INCORR_EXISTS_C) == approx(0)
        assert r.get(dfk.EVAL_INCORR_MISSING_C) == approx(0)
        assert r.get(dfk.EVAL_CORR_LINK_F) == approx(0)
        assert r.get(dfk.EVAL_CORR_NO_LINK_F) == approx(0)
        assert r.get(dfk.EVAL_INCORR_LINK_F) == approx(1)
        assert r.get(dfk.EVAL_INCORR_EXISTS_F) == approx(0)
        assert r.get(dfk.EVAL_INCORR_MISSING_F) == approx(0)
        assert r.get(dfk.EVAL_ACCURACY) == approx(0)

    def test_full(self, datadir):
        data = read_json(datadir + 'test_dataset.json').get('dataset')
        r = ReferenceMetricsResults(data)
        assert r.get(dfk.EVAL_REF_TOTAL) == approx(20)
        assert r.get(dfk.EVAL_CORR_LINK_C) == approx(9)
        assert r.get(dfk.EVAL_CORR_NO_LINK_C) == approx(2)
        assert r.get(dfk.EVAL_INCORR_LINK_C) == approx(5)
        assert r.get(dfk.EVAL_INCORR_EXISTS_C) == approx(3)
        assert r.get(dfk.EVAL_INCORR_MISSING_C) == approx(1)
        assert r.get(dfk.EVAL_CORR_LINK_F) == approx(0.45)
        assert r.get(dfk.EVAL_CORR_NO_LINK_F) == approx(0.1)
        assert r.get(dfk.EVAL_INCORR_LINK_F) == approx(0.25)
        assert r.get(dfk.EVAL_INCORR_EXISTS_F) == approx(0.15)
        assert r.get(dfk.EVAL_INCORR_MISSING_F) == approx(0.05)
        assert r.get(dfk.EVAL_ACCURACY) == approx(0.55)
