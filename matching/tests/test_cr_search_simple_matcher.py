from matching.cr_search_simple_matcher import Matcher


class TestSearchSimpleMatcher:

    def test_params(self):
        matcher = Matcher(50)
        assert matcher.min_score == 50
        assert matcher.excluded_dois == []

        matcher = Matcher(78, ['10.1234/bve847', '10.8907/451fR4'])
        assert matcher.min_score == 78
        assert matcher.excluded_dois == ['10.1234/bve847', '10.8907/451fr4']

    def test_match(self):
        matcher = Matcher(80)
        assert matcher.match(
            '[1]D. Tkaczyk, P. Szostek, M. Fedoryszak, P. J. Dendek, and Ł. ' +
            'Bolikowski,“CERMINE: automatic extraction of structured ' +
            'metadata from scientific literature,” International Journal on ' +
            'Document Analysis and Recognition (IJDAR), vol. 18, no. 4, pp. ' +
            '317–335, 2015.')[0] == '10.1007/s10032-015-0249-8'
        assert matcher.match(
            '[1] D. Tkaczyk, P. Szostek, M. Fedoryszak, P.J. Dendek, Ł. ' +
            'Bolikowski, International Journal on Document Analysis and ' +
            'Recognition (IJDAR) 18 (2015) 317.')[0] == \
            '10.1007/s10032-015-0249-8'
        assert matcher.match(
            'Nosek recently lead a project in which 270 scientists sought ' +
            'to replicate 100 different studies in psychology, all ' +
            'published in 2008 — 97 of which claimed to have found ' +
            'significant results — and in the end, two-thirds failed to ' +
            'replicate.')[0] is None
