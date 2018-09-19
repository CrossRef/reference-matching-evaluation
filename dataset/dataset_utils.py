import utils.data_format_keys as dfk


def get_target_gt_doi(item):
    return item[dfk.DATASET_TARGET_GT][dfk.CR_ITEM_DOI]


def get_target_test_doi(item):
    return item[dfk.DATASET_TARGET_TEST][dfk.CR_ITEM_DOI]
