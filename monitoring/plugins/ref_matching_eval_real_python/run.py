#!/usr/bin/env python3

import matching.cr_search_validation_matcher
import sys

from evaluation.link_metrics import LinkMetricsResults
from multiprocessing import Pool
from utils.utils import read_json, save_json

dataset = read_json(sys.argv[1])['dataset']

matcher = matching.cr_search_validation_matcher.Matcher(0.4, 0.34, [])
with Pool(10) as p:
    results = p.map(matcher.match,
                    [item.get('ref_string') for item in dataset])

for item, target in zip(dataset, results):
    item['target_test']['DOI'] = target[0]
save_json(dataset, sys.argv[2])

link_results = LinkMetricsResults(dataset)
print(','.join([str(link_results.get(m))
                for m in ['precision', 'recall', 'F1']]))
