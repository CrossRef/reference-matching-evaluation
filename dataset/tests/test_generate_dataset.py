import os

from dataset.generate_dataset import generate_target_gt, format_ref_string
from pytest import fixture
from utils.utils import read_json


@fixture
def datadir(request):
    filename = request.module.__file__
    test_dir, _ = os.path.split(filename)
    return test_dir + '/'


class TestCustomStyles:

    def test_generate_target_gt(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert generate_target_gt(record, []) == \
            {'DOI': '10.1007/s10032-015-0249-8'}
        assert generate_target_gt(record, ['publisher', 'type']) == \
            {'DOI': '10.1007/s10032-015-0249-8',
             'publisher': 'Springer Nature',
             'type': 'journal-article'}

    def test_format_ref_string(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert format_ref_string(record, 'apa') == \
            'Tkaczyk, D., Szostek, P., Fedoryszak, M., Dendek, P. J., & ' + \
            'Bolikowski, Ł. (2015). CERMINE: automatic extraction of ' + \
            'structured metadata from scientific literature. ' + \
            'International Journal on Document Analysis and Recognition ' + \
            '(IJDAR), 18(4), 317–335.'
        assert format_ref_string(record, 'chicago-author-date') == \
            'Tkaczyk, Dominika, Paweł Szostek, Mateusz Fedoryszak, Piotr ' + \
            'Jan Dendek, and Łukasz Bolikowski. 2015. “CERMINE: Automatic ' + \
            'Extraction of Structured Metadata from Scientific ' + \
            'Literature.” International Journal on Document Analysis and ' + \
            'Recognition (IJDAR) 18 (4) (July 3): 317–335.'
        assert format_ref_string(record, 'modern-language-association') == \
            'Tkaczyk, Dominika et al. “CERMINE: Automatic Extraction of ' + \
            'Structured Metadata from Scientific Literature.” ' + \
            'International Journal on Document Analysis and Recognition ' + \
            '(IJDAR) 18.4 (2015): 317–335.'
        assert format_ref_string(record, 'american-chemical-society') == \
            '(1) Tkaczyk, D.; Szostek, P.; Fedoryszak, M.; Dendek, P. J.; ' + \
            'Bolikowski, Ł. International Journal on Document Analysis ' + \
            'and Recognition (IJDAR) 2015, 18, 317–335.'
        assert format_ref_string(record, 'degraded_one_author') == \
            'Tkaczyk, Dominika. CERMINE: automatic extraction of ' + \
            'structured metadata from scientific literature. ' + \
            'International Journal on Document Analysis and Recognition ' + \
            '(IJDAR). 2015. 18. 4. 317-335'
        assert format_ref_string(record, 'degraded_title_scrambled') == \
            'Tkaczyk, Dominika, Szostek, Paweł, Fedoryszak, Mateusz, ' + \
            'Dendek, Piotr Jan, Bolikowski, Łukasz. automatic metadata ' + \
            'from scientific of literature CERMINE: extraction ' + \
            'structured. International Journal on Document Analysis and ' + \
            'Recognition (IJDAR). 2015. 18. 4. 317-335'
