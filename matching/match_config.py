import matching.cr_search_simple_matcher
import matching.cr_search_validation_matcher
import matching.stq_matcher
import matching.cr_search_year3_matcher

from utils.utils import read_json

# STQ matcher
# MATCHER = matching.stq_matcher.Matcher()

# SBM matcher without exclusion
# MATCHER = matching.cr_search_simple_matcher.Matcher(-1)

# SBM matcher with exclusion
excluded = 'data/relevance_threshold/samples/sample-excluded-2500.json'
MATCHER = matching.cr_search_simple_matcher.Matcher(-1, read_json(excluded)
                                                    ['sample_dois'])

# SBM matcher with exclusion and validation
#MATCHER = matching.cr_search_validation_matcher.Matcher(0.4, -1,
#                                                        read_json(excluded)
#                                                        ['sample_dois'])
