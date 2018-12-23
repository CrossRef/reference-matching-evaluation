import os

from dataset.extend_sample import similar_search_query
from pytest import fixture
from utils.utils import read_json


@fixture
def datadir(request):
    filename = request.module.__file__
    test_dir, _ = os.path.split(filename)
    return test_dir + '/'


class TestCustomStyles:

    def test_similar_search_query(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert similar_search_query(record) == \
            'CERMINE: automatic extraction of structured metadata from ' + \
            'scientific literature International Journal on Document ' + \
            'Analysis and Recognition (IJDAR) Tkaczyk Szostek Fedoryszak ' + \
            'Dendek Bolikowski'
