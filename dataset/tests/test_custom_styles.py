import os
import random

from dataset.custom_styles import get_authors, strip_stopwords, scramble, \
    get_journal_title, get_year, get_volume, get_issue, get_page, \
    degraded_all_authors, degraded_one_author, degraded_no_stopwords, \
    degraded_title_scrambled
from pytest import fixture
from utils.utils import read_json


@fixture
def datadir(request):
    filename = request.module.__file__
    test_dir, _ = os.path.split(filename)
    return test_dir + '/'


class TestCustomStyles:

    def test_get_authors(self, datadir):
        record = read_json(datadir + 'test_record.json')
        authors = 'Tkaczyk, Dominika, Szostek, Paweł, Fedoryszak, ' + \
            'Mateusz, Dendek, Piotr Jan, Bolikowski, Łukasz'
        assert get_authors(record) == authors

        record['author'] = record['author'] * 50
        assert get_authors(record) == ', '.join([authors] * 10)

        record['author'] = []
        assert get_authors(record) == ''

    def test_strip_stopwords(self):
        assert strip_stopwords('') == ''
        assert strip_stopwords('automatic extraction of structured metadata ' +
                               'from the scientific literature') == \
            'automatic extraction structured metadata scientific literature'

    def test_scramble(self):
        random.seed(10)
        assert scramble('automatic extraction of structured metadata from ' +
                        'the scientific literature') == \
            'from of scientific extraction literature metadata structured ' + \
            'the automatic'

    def test_get_journal_title(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert get_journal_title(record) == \
            'International Journal on Document Analysis and Recognition ' + \
            '(IJDAR)'

        record['container-title'] = []
        assert get_journal_title(record) == ''

        del record['container-title']
        assert get_journal_title(record) == ''

    def test_get_year(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert get_year(record) == '2015'

    def test_get_volume(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert get_volume(record) == '18'

    def test_get_issue(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert get_issue(record) == '4'

    def test_get_page(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert get_page(record) == '317-335'

    def test_degraded_all_authors(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert degraded_all_authors(record) == \
            'Tkaczyk, Dominika, Szostek, Paweł, Fedoryszak, Mateusz, ' + \
            'Dendek, Piotr Jan, Bolikowski, Łukasz. CERMINE: automatic ' + \
            'extraction of structured metadata from scientific ' + \
            'literature. International Journal on Document Analysis and ' + \
            'Recognition (IJDAR). 2015. 18. 4. 317-335'

    def test_degraded_one_author(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert degraded_one_author(record) == \
            'Tkaczyk, Dominika. CERMINE: automatic extraction of ' + \
            'structured metadata from scientific literature. ' + \
            'International Journal on Document Analysis and Recognition ' + \
            '(IJDAR). 2015. 18. 4. 317-335'

    def test_degraded_no_stopwords(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert degraded_no_stopwords(record) == \
            'Tkaczyk, Dominika, Szostek, Paweł, Fedoryszak, Mateusz, ' + \
            'Dendek, Piotr Jan, Bolikowski, Łukasz. CERMINE: automatic ' + \
            'extraction structured metadata scientific literature. ' + \
            'International Journal on Document Analysis and Recognition ' + \
            '(IJDAR). 2015. 18. 4. 317-335'

    def test_degraded_title_scrambled(self, datadir):
        record = read_json(datadir + 'test_record.json')
        random.seed(10)
        assert degraded_title_scrambled(record) == \
            'Tkaczyk, Dominika, Szostek, Paweł, Fedoryszak, Mateusz, ' + \
            'Dendek, Piotr Jan, Bolikowski, Łukasz. metadata extraction ' + \
            'scientific automatic literature structured of from CERMINE:. ' + \
            'International Journal on Document Analysis and Recognition ' + \
            '(IJDAR). 2015. 18. 4. 317-335'
