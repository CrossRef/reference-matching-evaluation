import utils.data_format_keys as dfk


def get_target_gt_doi(item):
    return item.get(dfk.DATASET_TARGET_GT, {}).get(dfk.CR_ITEM_DOI)


def get_target_test_doi(item):
    return item.get(dfk.DATASET_TARGET_TEST, {}).get(dfk.CR_ITEM_DOI)
