from matching.cr_search_validation_matcher import Matcher


class TestSearchValidationMatcher:

    def test_params(self):
        matcher = Matcher(0.5, 0.7)
        assert matcher.min_score == 0.5
        assert matcher.min_similarity == 0.7
        assert matcher.excluded_dois == []

        matcher = Matcher(0.78, 0.34, ['10.1234/bve847', '10.8907/451fR4'])
        assert matcher.min_score == 0.78
        assert matcher.min_similarity == 0.34
        assert matcher.excluded_dois == ['10.1234/bve847', '10.8907/451fr4']

    def test_match(self):
        matcher = Matcher(0.4, 0.34)

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

        assert matcher.match_structured(
            {'author': 'Tkaczyk',
             'article-title': 'CERMINE: automatic extraction of structured ' +
                              'metadata from scientific literature',
             'journal-title': 'International Journal on Document Analysis ' +
                              'and Recognition',
             'volume': '18',
             'issue': '4',
             'first-page': '317',
             'year': '2015'})[0] == '10.1007/s10032-015-0249-8'
        assert matcher.match_structured(
            {'author': 'Bolikowski',
             'article-title': 'Nosek recently lead a project',
             'journal-title': 'International Journal on Document Analysis ' +
                              'and Recognition',
             'first-page': '31',
             'year': '2016'})[0] is None

    def test_match_string(self):
        matcher = Matcher(0.4, 0.34)
        assert matcher.match_string(
            '[1]D. Tkaczyk, P. Szostek, M. Fedoryszak, P. J. Dendek, and Ł. ' +
            'Bolikowski,“CERMINE: automatic extraction of structured ' +
            'metadata from scientific literature,” International Journal on ' +
            'Document Analysis and Recognition (IJDAR), vol. 18, no. 4, pp. ' +
            '317–335, 2015.')[0] == '10.1007/s10032-015-0249-8'
        assert matcher.match_string(
            '[1] D. Tkaczyk, P. Szostek, M. Fedoryszak, P.J. Dendek, Ł. ' +
            'Bolikowski, International Journal on Document Analysis and ' +
            'Recognition (IJDAR) 18 (2015) 317.')[0] == \
            '10.1007/s10032-015-0249-8'
        assert matcher.match_string(
            'Nosek recently lead a project in which 270 scientists sought ' +
            'to replicate 100 different studies in psychology, all ' +
            'published in 2008 — 97 of which claimed to have found ' +
            'significant results — and in the end, two-thirds failed to ' +
            'replicate.')[0] is None

    def test_match_structured(self):
        matcher = Matcher(0.4, 0.34)
        assert matcher.match_structured(
            {'author': 'Tkaczyk',
             'article-title': 'CERMINE: automatic extraction of structured ' +
                              'metadata from scientific literature',
             'journal-title': 'International Journal on Document Analysis ' +
                              'and Recognition',
             'volume': '18',
             'issue': '4',
             'first-page': '317',
             'year': '2015'})[0] == '10.1007/s10032-015-0249-8'
        assert matcher.match_structured(
            {'author': 'Bolikowski',
             'article-title': 'Nosek recently lead a project',
             'journal-title': 'International Journal on Document Analysis ' +
                              'and Recognition',
             'first-page': '31',
             'year': '2016'})[0] is None

    def test_update_weights_all(self):
        matcher = Matcher(0.4, 0.34)
        cand_set = {}
        str_set = {}
        ref_numbers = ['90', '345', '1999', '2']

        matcher.update_weights_all('year', 'y: 1999', ref_numbers, cand_set,
                                   str_set)
        assert ref_numbers == ['90', '345', '2']
        assert cand_set == {'year_0': 1}
        assert str_set == {'year_0': 1}

        matcher.update_weights_all('volume', '23', ref_numbers, cand_set,
                                   str_set)
        assert ref_numbers == ['90', '345', '2']
        assert cand_set == {'year_0': 1, 'volume_0': 1}
        assert str_set == {'year_0': 1, 'volume_0': 0}

        matcher.update_weights_all('page', '345--348', ref_numbers, cand_set,
                                   str_set, weight=0.6)
        assert ref_numbers == ['90', '2']
        assert cand_set == \
            {'year_0': 1, 'volume_0': 1, 'page_0': 0.6, 'page_1': 0.6}
        assert str_set == \
            {'year_0': 1, 'volume_0': 0, 'page_0': 0.6, 'page_1': 0}

        matcher.update_weights_all('issue', 'metadata', ref_numbers, cand_set,
                                   str_set, weight=0.6)
        assert ref_numbers == ['90', '2']
        assert cand_set == \
            {'year_0': 1, 'volume_0': 1, 'page_0': 0.6, 'page_1': 0.6}
        assert str_set == \
            {'year_0': 1, 'volume_0': 0, 'page_0': 0.6, 'page_1': 0}

    def test_update_weights_one(self):
        matcher = Matcher(0.4, 0.34)
        cand_set = {}
        str_set = {}

        matcher.update_weights_one('year', 'y: 1999', '1999', cand_set,
                                   str_set)
        assert cand_set == {'year': 1}
        assert str_set == {'year': 1}

        matcher.update_weights_one('volume', '23', '25', cand_set, str_set)
        assert cand_set == {'year': 1, 'volume': 1}
        assert str_set == {'year': 1, 'volume': 0}

        matcher.update_weights_one('page', '345--348', '345', cand_set,
                                   str_set, weight=0.6)
        assert cand_set == {'year': 1, 'volume': 1, 'page': 0.6}
        assert str_set == {'year': 1, 'volume': 0, 'page': 0.6}

        matcher.update_weights_one('issue', '34', 'metadata', cand_set,
                                   str_set, weight=0.6)
        assert cand_set == {'year': 1, 'volume': 1, 'page': 0.6, 'issue': 0.3}
        assert str_set == {'year': 1, 'volume': 0, 'page': 0.6, 'issue': 0}
