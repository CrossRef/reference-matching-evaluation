from dataset.dataset_utils import get_target_gt_doi, get_target_test_doi


ITEM = \
    {'style': 'ieee',
     'ref_string': 'A very smart and influential paper.',
     'target_gt': {
         'DOI': '10.14195/2182-7087_2_1',
         'type': 'journal-article'
     },
     'target_test': {
         'DOI': '10.14195/2182-708',
         'type': 'journal-article'
     }}


class TestDatasetUtils:

    def test_target_gt_doi(self):
        assert get_target_gt_doi({}) is None
        assert get_target_gt_doi(ITEM) == '10.14195/2182-7087_2_1'

    def test_target_test_doi(self):
        assert get_target_test_doi({}) is None
        assert get_target_test_doi(ITEM) == '10.14195/2182-708'
