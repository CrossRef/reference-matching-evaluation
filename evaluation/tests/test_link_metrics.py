import os
import utils.data_format_keys as dfk

from evaluation.link_metrics import LinkMetricsResults
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


class TestLinkMetrics:

    def test_single_correct(self):
        r = LinkMetricsResults(SINGLE_CORRECT)
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(1)

    def test_single_incorrect(self):
        r = LinkMetricsResults(SINGLE_INCORRECT)
        assert r.get(dfk.EVAL_PREC) == approx(0)
        assert r.get(dfk.EVAL_REC) == approx(0)
        assert r.get(dfk.EVAL_F1) == approx(0)

    def test_full(self, datadir):
        data = read_json(datadir + 'test_dataset.json').get('dataset')
        r = LinkMetricsResults(data)
        assert r.get(dfk.EVAL_PREC) == approx(9/17)
        assert r.get(dfk.EVAL_REC) == approx(3/5)
        assert r.get(dfk.EVAL_F1) == approx(9/16)
