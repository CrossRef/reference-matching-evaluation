#!/usr/bin/env python3

import sys

from multiprocessing import Pool
from utils.cr_utils import get_item

with open(sys.argv[1]) as f:
    dois = f.readlines()
dois = [d.strip() for d in dois]

with Pool(10) as p:
    sample = p.map(get_item, dois)

references = [r for item in sample for r in item.get('reference', [])]
doi_publ = [r for r in references if r.get('doi-asserted-by') == 'publisher']
doi_cr_str = [r for r in references
              if r.get('doi-asserted-by') == 'crossref'
              and ('year' in r or 'author' in r)]
doi_cr_uns = [r for r in references
              if r.get('doi-asserted-by') == 'crossref'
              and 'year' not in r and 'author' not in r]
no_match_str = [r for r in references
                if 'DOI' not in r and ('year' in r or 'author' in r)]
no_match_uns = [r for r in references
                if 'DOI' not in r and 'year' not in r and 'author' not in r]

print('{},{}'.format(len(references),
                     ','.join([str(len(e)/len(references))
                               for e in [doi_publ, doi_cr_uns, doi_cr_str,
                                         no_match_uns, no_match_str]])))
