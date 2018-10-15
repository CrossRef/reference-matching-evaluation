# Reference matching experiments

The notebooks here contain various experiments related to reference matching algorithms.

Two approaches to reference matching are tested in these experiments:

  * **STQ**: the current approach based on Simple Text Query form
  * **SBM**: search-based matching, the new idea based on the search API

STQ uses regular expressions and reference parsing.

SBM is a very simple algorithm, which doesn't include any reference parsing step. In SBM the entire reference string is used as a query in the search engine. The first hit is returned as the matched target document, if its relevance score is high enough. If the relevance score of the first hit is low, no target DOI is assigned and the reference string stays unmatched.

The notebooks:

  * **relevance\_threshold**: experiments with the relevance score threshold (approaches and values) for SBM
  * **comparison**: evaluation and comparison of STQ and SBM
  * **existing\_matches**: comparison of existing links in the system against the current results of STQ and SBM
  * **sampling\_notes**: simple experiments related to sampling and confidence intervals
