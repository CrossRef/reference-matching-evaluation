from utils.utils import keep_fields, safe_div


class TestSafeDiv:

    def test_non_zero(self):
        assert safe_div(12, 3, 9) == 4
        assert safe_div(-12, 3, 9) == -4
        assert safe_div(0, 3, 9) == 0

    def test_zero(self):
        assert safe_div(12, 0, 9) == 9
        assert safe_div(0, 0, 9) == 9


class TestKeepFields:

    def test_empty(self):
        assert keep_fields({}, []) == {}
        assert keep_fields({}, ['a', 'b', 'c']) == {}

    def test(self):
        assert keep_fields({'a': 1, 'b': 2, 'c': 3}, []) == {}
        assert keep_fields({'a': 1, 'b': 2, 'c': 3}, ['a', 'c']) == \
            {'a': 1, 'c': 3}
        assert keep_fields({'a': 1, 'b': 2, 'c': 3}, ['a', 'c', 'd']) == \
            {'a': 1, 'c': 3}
