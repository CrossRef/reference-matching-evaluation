import os

from dataset.export_existing_and_new_links import is_unstructured, \
    is_structured, extract_refs
from pytest import fixture
from utils.utils import read_json


@fixture
def datadir(request):
    filename = request.module.__file__
    test_dir, _ = os.path.split(filename)
    return test_dir + '/'


class TestCustomStyles:

    def test_is_unstructured(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert is_unstructured(record['reference'][0])
        assert not is_unstructured(record['reference'][12])

    def test_is_structured(self, datadir):
        record = read_json(datadir + 'test_record.json')
        assert not is_structured(record['reference'][0])
        assert is_structured(record['reference'][12])

    def test_extract_refs(self, datadir):
        record = read_json(datadir + 'test_record.json')
        data = {'sample': [record, record]}
        assert len(extract_refs(data, is_unstructured)) == 70
        assert len(extract_refs(data, is_structured)) == 8
