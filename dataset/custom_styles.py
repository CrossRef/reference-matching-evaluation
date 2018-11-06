import utils.data_format_keys as dfk

from nltk.corpus import stopwords
from random import shuffle


cachedStopWords = stopwords.words('english')


def get_authors(rec, number=50):
    names = []
    for count, entry in enumerate(rec.get(dfk.CR_ITEM_AUTHOR, [])):
        family = entry.get(dfk.CR_ITEM_FAMILY, '')
        given = entry.get(dfk.CR_ITEM_GIVEN, '')
        name = family + ', ' + given
        names.append(name)
        if count + 1 == number:
            break
    return ', '.join(names)


def strip_stopwords(text):
    return ' '.join([word for word in text.split()
                     if word not in cachedStopWords])


def scramble(text):
    words = text.split()
    shuffle(words)
    return ' '.join(words)


def get_journal_title(record):
    try:
        return record.get(dfk.CR_ITEM_CONTAINER_TITLE, [''])[0]
    except IndexError:
        return ''


def get_year(record):
    issued = record['issued']['date-parts']
    if issued is not None and issued[0][0] is not None:
        return str(issued[0][0])
    return ''


def get_volume(record):
    return record.get('volume', '')


def get_issue(record):
    return record.get('issue', '')


def get_page(record):
    return record.get('page', '')


def degraded_all_authors(record):
    authors = get_authors(record)
    title = (record.get(dfk.CR_ITEM_TITLE, ['']))[0]
    journal = get_journal_title(record)
    ref = authors + '. ' + title + '. ' + journal + '. ' + \
        get_year(record) + '. ' + get_volume(record) + '. ' + \
        get_issue(record) + '. ' + get_page(record)
    return ref


def degraded_one_author(record):
    authors = get_authors(record, 1)
    title = (record.get(dfk.CR_ITEM_TITLE, ['']))[0]
    journal = get_journal_title(record)
    ref = authors + '. ' + title + '. ' + journal + '. ' + \
        get_year(record) + '. ' + get_volume(record) + '. ' + \
        get_issue(record) + '. ' + get_page(record)
    return ref


def degraded_no_stopwords(record):
    authors = get_authors(record)
    title = strip_stopwords((record.get(dfk.CR_ITEM_TITLE, ['']))[0])
    journal = get_journal_title(record)
    ref = authors + '. ' + title + '. ' + journal + '. ' + \
        get_year(record) + '. ' + get_volume(record) + '. ' + \
        get_issue(record) + '. ' + get_page(record)
    return ref


def degraded_title_scrambled(record):
    authors = get_authors(record)
    title = scramble((record.get(dfk.CR_ITEM_TITLE, ['']))[0])
    journal = get_journal_title(record)
    ref = authors + '. ' + title + '. ' + journal + '. ' + \
        get_year(record) + '. ' + get_volume(record) + '. ' + \
        get_issue(record) + '. ' + get_page(record)
    return ref


CUSTOM_STYLES = \
    {'degraded_all_authors': degraded_all_authors,
     'degraded_one_author': degraded_one_author,
     'degraded_no_stopwords': degraded_no_stopwords,
     'degraded_title_scrambled': degraded_title_scrambled}
