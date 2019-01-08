#!/usr/bin/env python3

import re
import sys

from dataset.draw_sample import generate_sample_data
from dataset.generate_dataset import generate_dataset
from utils.utils import save_json


sample = generate_sample_data(1000, {}, '')['sample']
dataset = generate_dataset(
    sample,
    ['apa', 'american-chemical-society', 'elsevier-without-titles',
     'chicago-author-date', 'modern-language-association',
     'degraded_one_author', 'degraded_title_scrambled'],
    [])

save_json(dataset, sys.argv[1])
with open(sys.argv[2], 'w') as file:
    file.write('\n'.join([re.sub('\s+', ' ', d['ref_string'])
                          for d in dataset]))
