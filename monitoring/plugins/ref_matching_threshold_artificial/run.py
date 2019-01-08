#!/usr/bin/env python3

import numpy as np
import matching.cr_search_validation_matcher
import utils.data_format_keys as dfk
import sys

from dataset.draw_sample import generate_sample_data
from dataset.generate_dataset import generate_dataset
from evaluation.link_metrics import LinkMetricsResults
from multiprocessing import Pool
from utils.utils import save_json


def modify_simple_threshold(dataset, threshold):
    for item in dataset:
        if item[dfk.DATASET_SCORE] is not None and \
                item[dfk.DATASET_SCORE] < threshold:
            item[dfk.DATASET_TARGET_TEST][dfk.CR_ITEM_DOI] = None
    return dataset


def find_best(results):
    overall = [r[1].get(dfk.EVAL_F1) for r in results]
    index = len(overall) - overall[::-1].index(max(overall)) - 1
    return index, results[index][0], results[index][1].get(dfk.EVAL_PREC), \
        results[index][1].get(dfk.EVAL_REC), results[index][1].get(dfk.EVAL_F1)


sample_pos = generate_sample_data(700, {}, '')['sample']
dataset_pos = generate_dataset(
    sample_pos,
    ['apa', 'american-chemical-society', 'elsevier-without-titles',
     'chicago-author-date', 'modern-language-association',
     'degraded_one_author', 'degraded_title_scrambled'],
    [])

sample_neg = generate_sample_data(700, {}, '')['sample']
dataset_neg = generate_dataset(
    sample_neg,
    ['apa', 'american-chemical-society', 'elsevier-without-titles',
     'chicago-author-date', 'modern-language-association',
     'degraded_one_author', 'degraded_title_scrambled'],
    [])
excluded = [item['target_gt']['DOI']for item in dataset_neg]
for item in dataset_neg:
    item['target_gt']['DOI'] = None

dataset = dataset_pos + dataset_neg

matcher = matching.cr_search_validation_matcher.Matcher(0.4, 0, excluded)
with Pool(10) as p:
    results = p.map(matcher.match,
                    [item.get('ref_string') for item in dataset])

for item, target in zip(dataset, results):
    item['target_test'] = {'DOI': target[0]}
    item['score'] = target[1]
save_json(dataset, sys.argv[1])

results_valid_threshold = \
    [(t, LinkMetricsResults(modify_simple_threshold(dataset, t)))
     for t in np.arange(0.0, 1.0, 0.01)]
print(','.join([str(i) for i in find_best(results_valid_threshold)[1:]]))
