import matching.cr_search_simple_matcher
import matching.stq_matcher

from utils.utils import read_json

# STQ matcher
# MATCHER = matching.stq_matcher.Matcher()

# SA matcher without exclusion
# MATCHER = matching.cr_search_simple_matcher.Matcher(-1)

# SA matcher with exclusion
MATCHER = matching.cr_search_simple_matcher.Matcher(
    -1, read_json('data/threshold/dataset-excluded-2500.json')
    ['dataset_dois'])
