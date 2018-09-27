import scipy.stats as st

from dataset.dataset_utils import get_target_gt_doi, get_target_test_doi
from statistics import mean


def doi_gt_null(item):
    return get_target_gt_doi(item) is None


def doi_test_null(item):
    return get_target_test_doi(item) is None


def doi_equals(item):
    if doi_gt_null(item) or doi_test_null(item):
        return get_target_gt_doi(item) == get_target_test_doi(item)
    return get_target_gt_doi(item).lower() == get_target_test_doi(item).lower()


def doi_gt_same(item, doi):
    if doi_gt_null(item) or doi is None:
        return get_target_gt_doi(item) == doi
    return get_target_gt_doi(item).lower() == doi.lower()


def doi_test_same(item, doi):
    if doi_test_null(item) or doi is None:
        return get_target_test_doi(item) == doi
    return get_target_test_doi(item).lower() == doi.lower()


def split_by_ref_attr(dataset, attr):
    split_values = set([d[attr] for d in dataset if d[attr] is not None])
    split_dataset = {v: [] for v in split_values}
    for item in dataset:
        if item[attr] is not None:
            split_dataset[item[attr]].append(item)
    return split_dataset


def confidence_interval(sample, confidence_level):
    if len(set(sample)) == 1:
        return sample[0], sample[0]
    return st.t.interval(confidence_level, len(sample)-1, loc=mean(sample),
                         scale=st.sem(sample))
