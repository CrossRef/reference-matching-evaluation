import matching.cr_search_simple_matcher
import matching.cr_search_validation_matcher
import matching.stq_matcher
import matching.openurl_query_matcher

# from utils.utils import read_json

# STQ matcher
# MATCHER = matching.stq_matcher.Matcher()

# Open URL matcher
# MATCHER = matching.openurl_query_matcher.Matcher()

# SBM matcher without exclusion
# MATCHER = matching.cr_search_simple_matcher.Matcher(
#    -1, journal_file='data/journal_abbreviations/journal-abbreviations.txt')

# SBM matcher with exclusion
# excluded = 'data/sbm_analysis/samples/sample-excluded-2500.json'
# MATCHER = matching.cr_search_simple_matcher.Matcher(-1, read_json(excluded)
#                                                    ['sample_dois'])

# SBM matcher with validation
MATCHER = matching.cr_search_validation_matcher.Matcher(
    0.4, -1, excluded_dois=[],
    journal_file='data/journal_abbreviations/journal-abbreviations.txt')

# SBM matcher with exclusion and validation
# excluded = 'data/sbm_analysis/samples/sample-excluded-2500.json'
# MATCHER = matching.cr_search_validation_matcher.Matcher(0.4, -1,
#                                                        read_json(excluded)
#                                                        ['sample_dois'])
