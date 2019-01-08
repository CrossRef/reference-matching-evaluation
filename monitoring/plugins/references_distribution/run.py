#!/usr/bin/env python3

import sys

from utils.cr_utils import get_sample
from utils.utils import save_json

sample = get_sample(10000, {'has-references': True})
save_json(sample, sys.argv[1])

references = [r for item in sample for r in item.get('reference', [])]
doi_publ = [r for r in references if r.get('doi-asserted-by') == 'publisher']
doi_cr_uns = [r for r in references
              if r.get('doi-asserted-by') == 'crossref'
              and 'unstructured' in r]
doi_cr_str = [r for r in references
              if r.get('doi-asserted-by') == 'crossref'
              and 'unstructured' not in r]
no_match_uns = [r for r in references
                if 'DOI' not in r and 'unstructured' in r]
no_match_str = [r for r in references
                if 'DOI' not in r and 'unstructured' not in r]

print(','.join([str(len(e)/len(references))
                for e in [doi_publ, doi_cr_uns, doi_cr_str, no_match_uns,
                          no_match_str]]))
