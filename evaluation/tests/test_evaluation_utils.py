from evaluation.evaluation_utils import doi_gt_null, doi_test_null, doi_same, \
    doi_equals, doi_gt_same, doi_test_same, split_by_ref_attr


DATASET = \
    [{'style': 'ieee',
      'ref_string': 'A very smart and influential paper.',
      'target_gt': {'DOI': '10.14195/2182-7087_2_1d'},
      'target_test': {'DOI': '10.14195/2182-7087_2_1D'}},
     {'style': 'ieee',
      'ref_string': 'A very smart and influential paper.',
      'target_gt': {'DOI': None},
      'target_test': {'DOI': '10.14195/2182-708'}},
     {'style': 'apa',
      'ref_string': 'A very smart and influential paper.',
      'target_gt': {'DOI': '10.14195/2182-7087_2_1'},
      'target_test': {'DOI': None}},
     {'style': 'ieee',
      'ref_string': 'A very smart and influential paper.',
      'target_gt': {'DOI': None},
      'target_test': {'DOI': None}},
     {'style': 'acs',
      'ref_string': 'A very smart and influential paper.',
      'target_gt': {'DOI': '10.14195/2182-7087_2_1d'},
      'target_test': {'DOI': '10.14195/2182-7087_2_1e'}}]


class TestEvaluationUtils:

    def test_doi_gt_null(self):
        assert not doi_gt_null(DATASET[0])
        assert doi_gt_null(DATASET[1])
        assert not doi_gt_null(DATASET[2])
        assert doi_gt_null(DATASET[3])

    def test_doi_test_null(self):
        assert not doi_test_null(DATASET[0])
        assert not doi_test_null(DATASET[1])
        assert doi_test_null(DATASET[2])
        assert doi_test_null(DATASET[3])

    def test_doi_same(self):
        assert doi_same(None, None)
        assert not doi_same(None, '10.14195/2182-7087_2_1d')
        assert not doi_same(None, ['10.14195/2182-7087_2_1d',
                                   '10.14195/2182-7087_2_1e'])
        assert not doi_same('10.14195/2182-7087_2_1d', None)
        assert doi_same('10.14195/2182-7087_2_1d', '10.14195/2182-7087_2_1D')
        assert not doi_same('10.14195/2182-7087_2_1d',
                            '10.14195/2182-7087_2_1e')
        assert doi_same('10.14195/2182-7087_2_1d',
                        ['10.14195/2182-7087_2_1d', '10.14195/2182-7087_2_1e'])
        assert not doi_same('10.14195/2182-7087_2_1f',
                            ['10.14195/2182-7087_2_1d',
                             '10.14195/2182-7087_2_1e'])

    def test_doi_equals(self):
        assert doi_equals(DATASET[0])
        assert not doi_equals(DATASET[1])
        assert not doi_equals(DATASET[2])
        assert doi_equals(DATASET[3])
        assert not doi_equals(DATASET[4])

    def test_doi_gt_same(self):
        assert doi_gt_same(DATASET[0], '10.14195/2182-7087_2_1d')
        assert not doi_gt_same(DATASET[0], '10.14195/2182-7087_2_1e')
        assert doi_gt_same(DATASET[1], None)
        assert not doi_gt_same(DATASET[1], '10.14195/2182-7087_2_1d')

    def test_doi_test_same(self):
        assert doi_test_same(DATASET[0], '10.14195/2182-7087_2_1d')
        assert not doi_test_same(DATASET[0], '10.14195/2182-7087_2_1e')
        assert doi_test_same(DATASET[2], None)
        assert not doi_test_same(DATASET[2], '10.14195/2182-7087_2_1d')

    def test_split_by_ref_attr(self):
        split_dataset = split_by_ref_attr(DATASET, 'style')
        assert len(split_dataset) == 3
        assert len(split_dataset['ieee']) == 3
        assert len(split_dataset['apa']) == 1
        assert len(split_dataset['acs']) == 1
