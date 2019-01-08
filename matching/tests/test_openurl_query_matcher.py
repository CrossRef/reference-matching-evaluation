from matching.openurl_query_matcher import Matcher


class TestOpenURLQueryMatcher:

    def test_match(self):
        matcher = Matcher()
        assert matcher.match(
            {'author': 'Tkaczyk',
             'article-title': 'CERMINE: automatic extraction of structured ' +
                              'metadata from scientific literature',
             'journal-title': 'International Journal on Document Analysis ' +
                              'and Recognition',
             'volume': '18',
             'issue': '4',
             'first-page': '317',
             'year': '2015'})[0] == '10.1007/s10032-015-0249-8'
        assert matcher.match(
            {'author': 'Bolikowski',
             'article-title': 'Nosek recently lead a project',
             'journal-title': 'International Journal on Document Analysis ' +
                              'and Recognition',
             'first-page': '31',
             'year': '2016'})[0] is None
