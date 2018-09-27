import os
import utils.data_format_keys as dfk

from pytest import approx, fixture
from utils.utils import read_json
from evaluation.split_metrics import DocAttrLinkMetricsResults, \
    SplitByDocAttrResults, SplitByRefAttrResults


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
        'type': 'book'
      }}]


@fixture
def datadir(request):
    filename = request.module.__file__
    test_dir, _ = os.path.split(filename)
    return test_dir + '/'


class TestDocAttrLinkMetrics:

    def test_single_correct(self):
        r = DocAttrLinkMetricsResults(SINGLE_CORRECT, 'type',
                                      'journal-article')
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(1)

    def test_single_incorrect(self):
        r = DocAttrLinkMetricsResults(SINGLE_INCORRECT, 'type',
                                      'journal-article')
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(0)
        assert r.get(dfk.EVAL_F1) == approx(0)

        r = DocAttrLinkMetricsResults(SINGLE_INCORRECT, 'type', 'book')
        assert r.get(dfk.EVAL_PREC) == approx(0)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(0)

    def test_full(self, datadir):
        data = read_json(datadir + 'test_dataset.json')['dataset']
        r = DocAttrLinkMetricsResults(data, 'type', 'journal-article')
        assert r.get(dfk.EVAL_PREC) == approx(1/2)
        assert r.get(dfk.EVAL_REC) == approx(2/3)
        assert r.get(dfk.EVAL_F1) == approx(4/7)

        r = DocAttrLinkMetricsResults(data, 'type', 'reference-entry')
        assert r.get(dfk.EVAL_PREC) == approx(1)
        assert r.get(dfk.EVAL_REC) == approx(1)
        assert r.get(dfk.EVAL_F1) == approx(1)


class TestSplitByDocAttrMetrics:

    def test_single_correct(self):
        r = SplitByDocAttrResults(SINGLE_CORRECT, 'type')
        r = r.get(dfk.EVAL_SPLIT_METRICS)
        assert r.shape == (1, 4)
        assert r['type'].tolist()[0] == 'journal-article'
        assert r['precision'].tolist()[0] == approx(1)
        assert r['recall'].tolist()[0] == approx(1)
        assert r['F1'].tolist()[0] == approx(1)

    def test_single_incorrect(self):
        r = SplitByDocAttrResults(SINGLE_INCORRECT, 'type')
        r = r.get(dfk.EVAL_SPLIT_METRICS)
        r = r.sort_values(by='type')
        assert r.shape == (2, 4)
        assert r['type'].tolist() == ['book', 'journal-article']
        assert r['precision'].tolist() == approx([0, 1])
        assert r['recall'].tolist() == approx([1, 0])
        assert r['F1'].tolist() == approx([0, 0])

    def test_full(self, datadir):
        data = read_json(datadir + 'test_dataset.json')['dataset']
        r = SplitByDocAttrResults(data, 'type')
        r = r.get(dfk.EVAL_SPLIT_METRICS)
        r = r.sort_values(by='type')
        assert r.shape == (3, 4)
        assert r['type'].tolist() == ['book-chapter', 'journal-article',
                                      'reference-entry']
        assert r['precision'].tolist() == approx([1/3, 1/2, 1])
        assert r['recall'].tolist() == approx([1/4, 2/3, 1])
        assert r['F1'].tolist() == approx([2/7, 4/7, 1])


class TestSplitByRefAttrMetrics:

    def test_single_correct(self):
        r = SplitByRefAttrResults(SINGLE_CORRECT, 'style',
                                  ['10.14195/2182-7087_2_1d'])
        split_r = r.get(dfk.EVAL_SPLIT_METRICS)
        assert split_r.shape == (1, 13)
        assert split_r['style'][0] == 'ieee'
        for col in ['correct ref links (fraction)', 'accuracy',
                    'average precision over target docs',
                    'average recall over target docs',
                    'average F1 over target docs',
                    'precision', 'recall', 'F1']:
            assert split_r[col][0] == approx(1)
        for col in ['correct missing ref links (fraction)',
                    'incorrect ref links (fraction)',
                    'incorrect existing ref links (fraction)',
                    'incorrect missing ref links (fraction)']:
            assert split_r[col][0] == approx(0)

    def test_single_incorrect(self):
        r = SplitByRefAttrResults(SINGLE_INCORRECT, 'style',
                                  ['10.14195/2182-7087_2_1',
                                   '10.14195/2182-708'])
        split_r = r.get(dfk.EVAL_SPLIT_METRICS)
        assert split_r.shape == (1, 13)
        assert split_r['style'][0] == 'ieee'
        for col in ['incorrect ref links (fraction)']:
            assert split_r[col][0] == approx(1)
        for col in ['average precision over target docs',
                    'average recall over target docs']:
            assert split_r[col][0] == approx(0.5)
        for col in ['correct ref links (fraction)',
                    'correct missing ref links (fraction)',
                    'accuracy', 'average F1 over target docs', 'precision',
                    'recall', 'F1', 'incorrect existing ref links (fraction)',
                    'incorrect missing ref links (fraction)']:
            assert split_r[col][0] == approx(0)

    def test_full(self, datadir):
        data = read_json(datadir + 'test_dataset.json')
        r = SplitByRefAttrResults(data['dataset'], 'style',
                                  data['dataset_dois'])
        split_r = r.get(dfk.EVAL_SPLIT_METRICS)
        assert split_r.shape == (2, 13)

        r = SplitByRefAttrResults(data['dataset'], 'style',
                                  ['10.1103/physrevb.67.134406',
                                   '10.1159/000408205',
                                   '10.1002/chin.199827068'])
        split_r = r.get(dfk.EVAL_SPLIT_METRICS)
        split_r = split_r.sort_values(by='style')
        assert split_r.shape == (2, 13)
        assert split_r['style'].tolist() == ['apa', 'ieee']
        assert split_r['correct ref links (fraction)'].tolist() \
            == approx([2/5, 1/2])
        assert split_r['correct missing ref links (fraction)'].tolist() \
            == approx([1/10, 1/10])
        assert split_r['incorrect ref links (fraction)'].tolist() \
            == approx([2/5, 1/10])
        assert split_r['incorrect existing ref links (fraction)'].tolist() \
            == approx([0, 3/10])
        assert split_r['incorrect missing ref links (fraction)'].tolist() \
            == approx([1/10, 0])
        assert split_r['accuracy'].tolist() == approx([5/10, 3/5])
        assert split_r['average precision over target docs'].tolist() \
            == approx([1, 2/3])
        assert split_r['average recall over target docs'].tolist() \
            == approx([2/3, 1])
        assert split_r['average F1 over target docs'].tolist() \
            == approx([2/3, 2/3])
        assert split_r['precision'].tolist() == approx([1/2, 5/9])
        assert split_r['recall'].tolist() == approx([4/9, 5/6])
