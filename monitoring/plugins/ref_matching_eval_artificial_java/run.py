#!/usr/bin/env python3

import sys

from evaluation.link_metrics import LinkMetricsResults
from utils.utils import read_json

dataset = read_json(sys.argv[1])
results = read_json(sys.argv[2])

for item, target in zip(dataset, results):
    item['target_test'] = {'DOI': target['DOI']}

link_results = LinkMetricsResults(dataset)
print(','.join([str(link_results.get(m))
                for m in ['precision', 'recall', 'F1']]))
