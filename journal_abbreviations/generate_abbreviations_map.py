import argparse
import re


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='calculate the journal abbreviations map')
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)

    args = parser.parse_args()

    with open(args.input, 'r') as f:
        content = f.readlines()
    content = [c.strip().split('\t') for c in content]
    content = [c for c in content if len(c) == 2 and c[0] and c[1]
               and c[0] != re.sub('[^a-z]', '', c[1])]
    stats = {}
    for abbr, full in content:
        if abbr not in stats:
            stats[abbr] = {}
        if full not in stats[abbr]:
            stats[abbr][full] = 0
        stats[abbr][full] = stats[abbr][full] + 1
    for abbr in list(stats.keys()):
        abbr_stats = stats[abbr]
        best_count = max(list(abbr_stats.values()))
        best = [c[0] for c in abbr_stats.items() if c[1] == best_count][0]
        if best_count == 1:
            del stats[abbr]
        else:
            stats[abbr] = best
    with open(args.output, 'w') as f:
        for abbr, full in stats.items():
            f.write('{}\t{}\n'.format(abbr, full))
