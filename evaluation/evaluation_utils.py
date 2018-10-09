import re
import scipy.stats as st

from dataset.dataset_utils import get_target_gt_doi, get_target_test_doi
from statistics import mean


def doi_gt_null(item):
    return get_target_gt_doi(item) is None


def doi_test_null(item):
    return get_target_test_doi(item) is None


def doi_equals(item):
    return doi_normalize(get_target_gt_doi(item)) == \
           doi_normalize(get_target_test_doi(item))


def doi_gt_same(item, doi):
    return doi_normalize(get_target_gt_doi(item)) == doi_normalize(doi)


def doi_test_same(item, doi):
    return doi_normalize(get_target_test_doi(item)) == doi_normalize(doi)


def doi_normalize(doi):
    if doi is None:
        return None
    return re.sub(';.*', '', re.sub('//', '/', doi.lower()))


def split_by_ref_attr(dataset, attr):
    split_values = set([d.get(attr)
                        for d in dataset if d.get(attr) is not None])
    split_dataset = {v: [] for v in split_values}
    for item in dataset:
        if item[attr] is not None:
            split_dataset[item.get(attr)].append(item)
    return split_dataset


def confidence_interval(sample, confidence_level):
    if len(set(sample)) == 1:
        return sample[0], sample[0]
    return st.t.interval(confidence_level, len(sample)-1, loc=mean(sample),
                         scale=st.sem(sample))
