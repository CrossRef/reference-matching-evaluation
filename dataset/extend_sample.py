import argparse
import logging
import utils.data_format_keys as dfk

from dataset.draw_sample import read_sample_data, save_sample_data
from utils.cr_utils import search
from utils.utils import init_logging, timestamp


def similar_search_query(item):
    query = ''
    if dfk.CR_ITEM_TITLE in item:
        query = query + ' '.join(item[dfk.CR_ITEM_TITLE])
    if dfk.CR_ITEM_CONTAINER_TITLE in item:
        query = query + ' ' + ' '.join(item[dfk.CR_ITEM_CONTAINER_TITLE])
    if dfk.CR_ITEM_AUTHOR in item:
        query = query + ' ' + ' '.join([a[dfk.CR_ITEM_FAMILY]
                                        for a in item[dfk.CR_ITEM_AUTHOR]
                                        if dfk.CR_ITEM_FAMILY in a])
    return query


def search_similar_items(sample, n):
    logging.info('Searching for similar items')
    similar_items = []
    for item in sample:
        query = similar_search_query(item)
        similar_items = search(query)
        if similar_items is None:
            continue
        added = 0
        for similar_item in similar_items:
            if added >= n:
                break
            if similar_item[dfk.CR_ITEM_DOI] == item[dfk.CR_ITEM_DOI]:
                continue
            logging.debug('For item {} added similar item: {}'
                          .format(item[dfk.CR_ITEM_DOI],
                                  similar_item[dfk.CR_ITEM_DOI]))
            similar_items.append(similar_item)
            added = added + 1
    return similar_items


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='add similar records to existing sample')
    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_true')
    parser.add_argument('-s', '--sample', help='input sample file',
                        type=str, required=True)
    parser.add_argument('-e', '--extend',
                        help='the number of similar items per item to add',
                        type=int, required=True)
    parser.add_argument('-o', '--output', help='output sample file',
                        type=str, required=True)
    args = parser.parse_args()

    init_logging(args.verbose)

    sample_data = read_sample_data(args.sample)
    similar_records = \
        search_similar_items(sample_data[dfk.SAMPLE_SAMPLE], args.extend)
    extended_sample_data = sample_data
    extended_sample_data[dfk.SAMPLE_TIMESTAMP] = timestamp()
    extended_sample_data[dfk.SAMPLE_SIZE] = \
        sample_data[dfk.SAMPLE_SIZE] + len(similar_records)
    extended_sample_data[dfk.SAMPLE_SAMPLE] = \
        sample_data[dfk.SAMPLE_SAMPLE] + similar_records
    save_sample_data(extended_sample_data, args.output)
