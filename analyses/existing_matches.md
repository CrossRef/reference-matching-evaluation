
# Comparing existing and new links

Dominika Tkaczyk

13.10.2018

In this analysis I examine how the links existing in the live system compare to the links currently returned by both STQ and SBM algorithms.

For the comparison of the two algorithms on artificial data, see [this notebook](https://github.com/CrossRef/reference-matching-evaluation/blob/master/analyses/comparison.ipynb).

## TL;DR

  * I examined 100 random reference strings from the live system.
  * 46% of reference strings are currently unmatched in the system:
    * of those unmatched, in 32% cases STQ returned DOI
    * of those unmatched, in 30% cases STQ DOI is the same as SBM (almost every DOI returned by STQ was "confirmed" by SBM)
    * according to the estimations, when STQ did not give any answer, SA was correct in 16% cases
  * The remaining 54% of reference strings are currently matched in the system:
    * of those matched, in 89% cases all three links are the same; this confirms high agreement of STQ and SBM
    * of those matched, in 6% of the references STQ link is missing, but the original link is the same as SBM
    * of those matched, in 3% of the cases SA link is incorrect; the most common causes are:
      * a short reference string without the title
      * choosing a document closely related to the real target, such that usually contains all the real target's metadata, such as a review or a chapter instead of the book

## Methodology

The following procedure was used to gather the data for this experiment:
1. A sample of 5000 items was extracted from the system.
2. I iterated over all references in the sampled items, and extracted all 6289 unstructured references (reference strings).
3. ! sampled 1000 unstructured references from them and ran both STQ and SBM algorithms on them.
4. I examined the differences between the links.

## Results


```python
import sys
sys.path.append('..')

%matplotlib inline

import json
import matplotlib.pyplot as plt

from utils.utils import read_json, save_json

DATA_DIR = '../data/existing_links/'
```

Let's read the data:


```python
data = read_json(DATA_DIR + 'sample_1000.json')
orig_link = 'original_link'
stq_link = 'current_STQ_link'
sbm_link = 'search_API_link'
print(json.dumps(data[0], indent=4))
```

    {
        "source_DOI": "10.1007/978-3-319-40773-9_4",
        "ref_string": "Portocarrero, C. (2013a). Mapas de vulnerabilidad y riesgo de la subcuenca Chucch\u00fan ante la posible ocurrencia de un proceso aluvi\u00f3nico procedente de la Laguna 513. Huaraz: CARE Per\u00fa, Proyecto Glaciares.",
        "original_link": null,
        "current_STQ_link": null,
        "search_API_link": "10.19083/tesis/621436",
        "search_API_score": 69.07092,
        "reason": "original link null; STQ link null; SBM link incorrect"
    }


For each reference, I keep the following information:
  * source DOI
  * reference string
  * original link: link currently existing in the system, can be null
  * current STQ link: link obtained from STQ, can be null
  * search API link: link obtained from SBM, can be null
  * search API score: relevance score from SBM

### Null original link

The first category we will explore are references currently not matched to any target document in the system. How many references don't have the original link?


```python
data_orig_null = [d for d in data if d[orig_link] is None]
print('Null original link: {}'.format(len(data_orig_null)))
```

    Null original link: 459


45.9% of reference strings in our sample are not linked to anything. In how many cases we have a new STQ link?


```python
data_orig_null_stq_exists = [d for d in data_orig_null if d[stq_link] is not None]
print('Null original link, STQ link exists: {}'.format(len(data_orig_null_stq_exists)))
```

    Null original link, STQ link exists: 147


In 32.03% of references with null original link we have the new STQ link. And how many of those have the same SBM link?


```python
data_orig_null_sbm_stq_equal = [d for d in data_orig_null if d[stq_link] is not None and d[stq_link] == d[sbm_link]]
print('Null original link; STQ and SBM agree: {}'.format(len(data_orig_null_sbm_stq_equal)))
```

    Null original link; STQ and SBM agree: 139


It seems there is a high agreement between STQ and SBM, almost all new STQ links were "confirmed" by SBM.

We are left with 320 cases, in which the original link is null and STQ and SBM links differs. I manually inspected a sample of them and provided an explanation of what happened. This function will show the distribution of those explanations ("comments"):


```python
def summarize_comments(data):
    reasons = [d['reason'] for d in data]
    reasons = list(set([(r, reasons.count(r)) for r in reasons]))
    reasons.sort(key=lambda x: x[1], reverse=True) 
    return reasons 
```

The distribution of the explanations of the cases where original link is null and SBM and STQ links disagree:


```python
data_orig_null_sbm_stq_disagree = [d for d in data_orig_null if d[stq_link] != d[sbm_link]]
summarize_comments(data_orig_null_sbm_stq_disagree)
```




    [('original link null; STQ link null; SBM link not inspected', 185),
     ('original link null; STQ link null; SBM link incorrect', 104),
     ('original link null; STQ link null; SBM link correct', 20),
     ('original link null; STQ link null; SBM links to a review', 3),
     ('original link null; STQ and SBM disagree; same metadata', 2),
     ('original link null; STQ and SBM disagree; same landing page', 2),
     ('original link null; STQ and SBM disagree, SBM link broken', 1),
     ('original link null; STQ and SBM disagree; SBM link incorrect', 1),
     ('original link null; STQ and SBM disagree; SBM links to a chapter', 1),
     ('original link null; STQ and SBM disagree; SBM correct', 1)]



We have the following cases:
  * 185: only SBM link present; not inspected manually
  * 107: only SBM link present and incorrect 
  * 20: only SBM present and correct
  * 4: STQ and SBM links disagree, but the either the landing pages or the document metadata are the same
  * 4 other cases

### All links agree

How many cases we have, in which all three links agree?


```python
data_all_agree = [d for d in data
                  if d[orig_link] is not None and d[orig_link] == d[stq_link] and d[sbm_link] == d[stq_link]]
print('All links agree: {}'.format(len(data_all_agree)))
```

    All links agree: 481


Almost half of all the cases, and 89% of the cases with not null original link. This also confirms large agreement between STQ and SBM.

### Original link is different

In how many cases SBM link is the same as STQ link, but original link is not null and different?


```python
data_diff_orig = [d for d in data
                  if d[orig_link] is not None and d[orig_link] != d[stq_link] and d[sbm_link] == d[stq_link]]
print('Original link is different : {}'.format(len(data_diff_orig)))
summarize_comments(data_diff_orig)
```

    Original link is different : 2





    [('original link incorrect', 1), ('different version of the paper', 1)]



Only 2 references:
  * in one case the DOIs link to two different versions of the same paper (with identical metadata)
  * in the second case the original link is incorrect

### STQ link is different
  
Now let's see the cases, where original and SBM links agree and STQ is different:


```python
data_diff_stq = [d for d in data
                 if d[orig_link] is not None and d[orig_link] != d[stq_link] and d[sbm_link] == d[orig_link]]
print('STQ link is different : {}'.format(len(data_diff_stq)))
summarize_comments(data_diff_stq)
```

    STQ link is different : 31





    [('STQ link missing', 31)]



In all cases STQ link is simply missing.

### SBM link is different

How many cases we have, where SBM link is different from the other two?


```python
data_diff_sbt = [d for d in data
                if d[orig_link] is not None and d[orig_link] == d[stq_link] and d[sbm_link] != d[orig_link]]
print('SBT link is different : {}'.format(len(data_diff_sbt)))
summarize_comments(data_diff_sbt)
```

    SBT link is different : 24





    [('SBM link incorrect', 14),
     ('same document (metadata)', 3),
     ('same document (landing page)', 2),
     ('SBM links to a chapter', 2),
     ('SBM links to a correction', 1),
     ('original link incorrect', 1),
     ('SBM links to one paper in conference proceedings', 1)]



Out of 24 cases:
  * in 14 cases SBM link is incorrect (11 of those are strings not containing the title of the reference)
  * in 5 cases DOIs are the same or link to the same document
  * in 4 cases SBM links to a document related to the correct one, such as a chapter or a correction
  * in 1 case the original link is incorrect

### All three links are different


```python
data_diff_all = [d for d in data
                 if d[orig_link] is not None and d[orig_link] != d[stq_link]
                 and d[sbm_link] != d[orig_link] and d[stq_link] != d[sbm_link]]
print('All links different : {}'.format(len(data_diff_all)))
summarize_comments(data_diff_all)
```

    All links different : 3





    [('STQ link missing; both link to a different chapter', 2),
     ('STQ link missing; SBM link incorrect', 1)]



In all three cases STQ link is missing and SBT link is incorrect.

Finally, let's see the overall distribution of all 1000 cases:


```python
labels = 'all links agree', 'stq null; orig and SBM agree', 'orig null; STQ and SBM agree', \
         'orig null; STQ and SBM disagree', 'other cases'
sizes = [481, 29, 139, 320, 31]

fig, ax = plt.subplots(figsize=(9,6))
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
       colors=['#d8d2c4', '#4f5858', '#3eb1c8', '#ffc72c', '#ef3340'])
ax.axis('equal')

plt.show()
```


![png](existing_matches_files/existing_matches_34_0.png)

