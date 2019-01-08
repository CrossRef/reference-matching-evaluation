#!/usr/bin/env python3

import matching.cr_search_validation_matcher
import sys

from dataset.draw_sample import generate_sample_data
from dataset.generate_dataset import generate_dataset
from evaluation.link_metrics import LinkMetricsResults
from multiprocessing import Pool
from utils.utils import save_json

sample = generate_sample_data(1000, {}, '')['sample']
dataset = generate_dataset(
    sample,
    ['apa', 'american-chemical-society', 'elsevier-without-titles',
     'chicago-author-date', 'modern-language-association',
     'degraded_one_author', 'degraded_title_scrambled'],
    [])

matcher = matching.cr_search_validation_matcher.Matcher(0.4, 0.34, [])
with Pool(10) as p:
    results = p.map(matcher.match,
                    [item.get('ref_string') for item in dataset])

for item, target in zip(dataset, results):
    item['target_test'] = {'DOI': target[0]}
save_json(dataset, sys.argv[1])

link_results = LinkMetricsResults(dataset)
print(','.join([str(link_results.get(m))
                for m in ['precision', 'recall', 'F1']]))
