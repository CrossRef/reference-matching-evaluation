import argparse
import re
import utils.data_format_keys as dfk

from multiprocessing import Pool
from random import sample
from utils.utils import read_json
from utils.cr_utils import get_item


def extract_references(sample_works):
    references = []
    for work in sample_works.get(dfk.SAMPLE_SAMPLE):
        source_doi = work.get(dfk.CR_ITEM_DOI)
        for ref in work.get(dfk.CR_ITEM_REFERENCE, []):
            ref['source_DOI'] = source_doi
            references.append(ref)
    return references


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='extract journal abbreviations')
    parser.add_argument('-s', '--sample', type=str, required=True)
    parser.add_argument('-n', '--references', type=int, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)

    args = parser.parse_args()

    sample_data = read_json(args.sample)
    references = extract_references(sample_data)
    references = [r for r in references if 'DOI' in r and 'journal-title' in r]
    references = sample(references, args.references)

    with Pool(10) as p:
        results = p.map(get_item, [r['DOI'] for r in references])
    results = [r.get('container-title', [])
               if r is not None else '' for r in results]
    results = [r[0] if r else '' for r in results]

    with open(args.output, 'w') as f:
        for q, w in zip(references, results):
            a = re.sub('[^a-z]', '', q['journal-title'].lower())
            b = w.lower()
            if a and b and a != b:
                f.write('{}\t{}\n'.format(a, b))
