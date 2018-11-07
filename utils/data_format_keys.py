# fields of items from Crossref API
CR_ITEM_DOI = 'DOI'
CR_ITEM_SCORE = 'score'
CR_ITEM_TITLE = 'title'
CR_ITEM_CONTAINER_TITLE = 'container-title'
CR_ITEM_AUTHOR = 'author'
CR_ITEM_FAMILY = 'family'
CR_ITEM_GIVEN = 'given'
CR_ITEM_REFERENCE = 'reference'
CR_ITEM_DOI_ASSERTED_BY = 'doi-asserted-by'
CR_ITEM_UNSTRUCTURED = 'unstructured'

# fields of the sample
SAMPLE_TIMESTAMP = 'timestamp'
SAMPLE_FILTER = 'filter'
SAMPLE_QUERY = 'query'
SAMPLE_SIZE = 'size'
SAMPLE_DOIS = 'sample_dois'
SAMPLE_ORIGINAL_SIZE = 'original_size'
SAMPLE_SAMPLE = 'sample'

# fields of the dataset
DATASET_REF_ID = 'ref_id'
DATASET_TARGET_GT = 'target_gt'
DATASET_TARGET_TEST = 'target_test'
DATASET_STYLE = 'style'
DATASET_REF_STRING = 'ref_string'
DATASET_MATCHER = 'matcher'
DATASET_SCORE = 'score'
DATASET_DOIS = 'dataset_dois'
DATASET_DATASET = 'dataset'

# evaluation fields
EVAL_REF_TOTAL = 'number of references'

EVAL_CORR_LINK_C = 'correct ref links (count)'
EVAL_CORR_NO_LINK_C = 'correct missing ref links (count)'
EVAL_INCORR_LINK_C = 'incorrect ref links (count)'
EVAL_INCORR_EXISTS_C = 'incorrect existing ref links (count)'
EVAL_INCORR_MISSING_C = 'incorrect missing ref links (count)'

EVAL_CORR_LINK_F = 'correct ref links (fraction)'
EVAL_CORR_NO_LINK_F = 'correct missing ref links (fraction)'
EVAL_INCORR_LINK_F = 'incorrect ref links (fraction)'
EVAL_INCORR_EXISTS_F = 'incorrect existing ref links (fraction)'
EVAL_INCORR_MISSING_F = 'incorrect missing ref links (fraction)'

EVAL_ACCURACY = 'accuracy'
EVAL_CI_ACCURACY = 'confidence interval for accuracy'

EVAL_PREC = 'precision'
EVAL_REC = 'recall'
EVAL_F1 = 'F1'

EVAL_MEAN_PREC = 'average precision over target docs'
EVAL_MEAN_REC = 'average recall over target docs'
EVAL_MEAN_F1 = 'average F1 over target docs'

EVAL_CI_PREC = 'confidence interval for precision'
EVAL_CI_REC = 'confidence interval for recall'
EVAL_CI_F1 = 'confidence interval for F1'

EVAL_DOC_METRICS = 'link-based metrics for documents'
EVAL_SPLIT_METRICS = 'all metrics for split attribute values'
EVAL_SPLIT_DOC_METRICS = \
    'link-based metrics for documents for split attribute values'
