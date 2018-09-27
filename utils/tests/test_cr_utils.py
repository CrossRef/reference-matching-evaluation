from utils.cr_utils import generate_sample_args, parse_filter_text


class TestGenerateSampleArgs:

    def test_generate_sample_args(self):
        assert generate_sample_args(0) == []
        assert generate_sample_args(1, 'f', 'q') == [(1, 'f', 'q')]
        assert generate_sample_args(78, 2) == [(78, 2, {})]
        assert generate_sample_args(100) == [(100, {}, {})]
        assert generate_sample_args(101, 1, '4') == [(100, 1, '4'),
                                                     (1, 1, '4')]
        assert generate_sample_args(211) == [(100, {}, {}), (100, {}, {}),
                                             (11, {}, {})]


class TestParseFilterText:

    def test_parse_filter_text(self):
        assert parse_filter_text(None) == {}
        assert parse_filter_text('') == {}
        assert parse_filter_text('a:1') == {'a': '1'}
        assert parse_filter_text('a:1,bc:d,123:qqqq') == \
            {'a': '1', 'bc': 'd', '123': 'qqqq'}
