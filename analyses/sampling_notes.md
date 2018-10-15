
# Notes on sampling

Dominika Tkaczyk

4.09.2018

This notebook contains some basic experiments related to data sampling. The main purpose of this is to convince myself (and hopefully wider audience) that we can safely calculate things on samples of the data rather than on all the data.

## Introduction

First let's define some basic terms:
  * **population** - this is the complete set of "items" or "things" we are interested in. In statistics this is often a group of people (hence the term), for example the entire population of USA. In my experiments, the population is the entire set of metadata records (works) in Crossref system (100M records).
  * **sample** - a subset of items randomly chosen from the population. Its most important parameter is the size.
  * **statistic** - a numeric feature of the item. Examples: the age of a person, the number of authors listed in the metadata record, the length of the title.
  * **population average** - the average value of a statistic in the population.
  * **sample average** - the average value of a statistic in the sample.

In these experiments, we want to know the population average of a certain statistic. Depending on the size of the population, and how difficult it is to calculate the statistic, calculating the population average directly might not be fast enough or even possible. In such cases, one alternative is to use sampling to estimate the population average. Note that estimating =/= guessing.

Let's import some stuff.


```python
from crossref.restful import Works, Etiquette
from statistics import mean, stdev

import json
import math
import matplotlib.pyplot as plt
import numpy
import pandas as pd
import re
import scipy.stats as st
import tarfile
```

I will also politely introduce myself to Crossref API.


```python
works = Works(etiquette=Etiquette('Dominika\'s experiments', '0.1', '', 'dtkaczyk@crossref.org'))
```

## Estimating the average number of references

I chose a very simple statistic to play with: the number of references, as reported by *references-count* field in the metadata record. Later, I will do some additional experiments with a more complicated statistic.


```python
def ref_count(work):
    return work['references-count']
```

### The exact number

The average number of references over the entire population can be, of course, calculated directly. It takes about 3 hours to iterate over the entire dataset (without parallel processing). This code needs access to snapshot of the data:


```python
def iterate_files(filename):
    tar = tarfile.open(filename, 'r:gz')
    for member in tar:
        f = tar.extractfile(member)
        if f is not None:
            yield json.load(f)

def iterate_items(filename):
    for f in iterate_files(filename):
        for item in f['items']:
            yield item

records = 1e8
count = 0
total = 0
for item in iterate_items('/srv/data/snapshots/data-2018-08.tar.gz'):
    total = total + ref_count(item)
    count = count + 1
    if count % 1e4 == 0:
        print('{}% done (average ref count so far {:.4f})'.format(100*count/records, total/count))
```

    0.01% done (average ref count so far 0.0031)
    0.02% done (average ref count so far 0.0015)
    0.03% done (average ref count so far 0.0010)
    0.04% done (average ref count so far 0.0008)
    0.05% done (average ref count so far 0.0006)
    0.06% done (average ref count so far 0.0006)
    0.07% done (average ref count so far 0.0005)
    0.08% done (average ref count so far 0.0004)
    0.09% done (average ref count so far 0.0004)
    0.1% done (average ref count so far 0.0003)
    0.11% done (average ref count so far 0.0003)
    0.12% done (average ref count so far 0.0003)
    0.13% done (average ref count so far 0.0003)
    0.14% done (average ref count so far 0.0002)
    0.15% done (average ref count so far 0.0002)
    0.16% done (average ref count so far 0.0002)
    0.17% done (average ref count so far 0.0002)
    0.18% done (average ref count so far 0.0002)
    0.19% done (average ref count so far 0.0002)
    0.2% done (average ref count so far 0.0002)
    0.21% done (average ref count so far 0.0002)
    0.22% done (average ref count so far 0.0002)
    0.23% done (average ref count so far 0.0001)
    0.24% done (average ref count so far 0.0196)
    0.25% done (average ref count so far 0.0188)
    0.26% done (average ref count so far 0.0181)
    0.27% done (average ref count so far 0.0174)
    0.28% done (average ref count so far 0.0168)
    0.29% done (average ref count so far 0.0162)
    0.3% done (average ref count so far 0.0157)
    0.31% done (average ref count so far 0.0152)
    0.32% done (average ref count so far 0.0147)
    0.33% done (average ref count so far 0.0143)
    0.34% done (average ref count so far 0.0139)
    0.35% done (average ref count so far 0.0135)
    0.36% done (average ref count so far 0.0131)
    0.37% done (average ref count so far 0.0127)
    0.38% done (average ref count so far 0.0124)
    0.39% done (average ref count so far 0.0121)
    0.4% done (average ref count so far 0.0118)
    0.41% done (average ref count so far 0.0115)
    0.42% done (average ref count so far 0.0112)
    0.43% done (average ref count so far 0.0110)
    0.44% done (average ref count so far 0.0107)
    0.45% done (average ref count so far 0.0105)
    0.46% done (average ref count so far 0.0102)
    0.47% done (average ref count so far 0.0100)
    0.48% done (average ref count so far 0.0098)
    0.49% done (average ref count so far 0.0096)
    0.5% done (average ref count so far 0.0094)
    0.51% done (average ref count so far 0.0149)
    0.52% done (average ref count so far 0.0146)
    0.53% done (average ref count so far 0.0143)
    0.54% done (average ref count so far 0.0140)
    0.55% done (average ref count so far 0.0138)
    0.56% done (average ref count so far 0.0136)
    0.57% done (average ref count so far 0.0134)
    0.58% done (average ref count so far 0.0201)
    0.59% done (average ref count so far 0.0403)
    0.6% done (average ref count so far 0.0921)
    0.61% done (average ref count so far 0.3559)
    0.62% done (average ref count so far 0.7003)
    0.63% done (average ref count so far 0.9642)
    0.64% done (average ref count so far 1.2084)
    0.65% done (average ref count so far 1.4998)
    0.66% done (average ref count so far 1.6319)
    0.67% done (average ref count so far 1.8044)
    0.68% done (average ref count so far 1.9581)
    0.69% done (average ref count so far 2.0663)
    0.7% done (average ref count so far 2.3165)
    0.71% done (average ref count so far 2.5473)
    0.72% done (average ref count so far 2.6996)
    0.73% done (average ref count so far 2.8517)
    0.74% done (average ref count so far 2.9678)
    0.75% done (average ref count so far 3.0606)
    0.76% done (average ref count so far 3.1528)
    0.77% done (average ref count so far 3.2461)
    0.78% done (average ref count so far 3.3567)
    0.79% done (average ref count so far 3.3624)
    0.8% done (average ref count so far 3.4432)
    0.81% done (average ref count so far 3.5243)
    0.82% done (average ref count so far 3.6195)
    0.83% done (average ref count so far 3.8437)
    0.84% done (average ref count so far 4.0065)
    0.85% done (average ref count so far 4.3335)
    0.86% done (average ref count so far 4.8811)
    0.87% done (average ref count so far 4.9407)
    0.88% done (average ref count so far 4.9124)
    0.89% done (average ref count so far 4.8805)
    0.9% done (average ref count so far 4.8492)
    0.91% done (average ref count so far 4.8178)
    0.92% done (average ref count so far 4.7858)
    0.93% done (average ref count so far 4.7544)
    0.94% done (average ref count so far 4.7225)
    0.95% done (average ref count so far 4.7032)
    0.96% done (average ref count so far 4.6786)
    0.97% done (average ref count so far 4.8399)
    0.98% done (average ref count so far 5.0031)
    0.99% done (average ref count so far 5.1938)
    1.0% done (average ref count so far 5.3752)
    1.01% done (average ref count so far 5.4540)
    1.02% done (average ref count so far 5.6089)
    1.03% done (average ref count so far 5.9287)
    1.04% done (average ref count so far 6.4061)
    1.05% done (average ref count so far 6.8888)
    1.06% done (average ref count so far 7.1605)
    1.07% done (average ref count so far 7.2104)
    1.08% done (average ref count so far 7.2828)
    1.09% done (average ref count so far 7.2878)
    1.1% done (average ref count so far 7.2886)
    1.11% done (average ref count so far 7.3550)
    1.12% done (average ref count so far 7.5879)
    1.13% done (average ref count so far 8.0164)
    1.14% done (average ref count so far 8.4406)
    1.15% done (average ref count so far 8.6543)
    1.16% done (average ref count so far 8.6335)
    1.17% done (average ref count so far 8.8929)
    1.18% done (average ref count so far 8.9889)
    1.19% done (average ref count so far 8.9133)
    1.2% done (average ref count so far 8.9708)
    1.21% done (average ref count so far 9.1717)
    1.22% done (average ref count so far 9.3288)
    1.23% done (average ref count so far 9.2693)
    1.24% done (average ref count so far 9.2956)
    1.25% done (average ref count so far 9.3980)
    1.26% done (average ref count so far 9.6658)
    1.27% done (average ref count so far 9.6745)
    1.28% done (average ref count so far 9.7110)
    1.29% done (average ref count so far 9.6774)
    1.3% done (average ref count so far 9.6322)
    1.31% done (average ref count so far 9.7055)
    1.32% done (average ref count so far 9.7961)
    1.33% done (average ref count so far 9.8293)
    1.34% done (average ref count so far 9.8532)
    1.35% done (average ref count so far 10.0284)
    1.36% done (average ref count so far 10.1213)
    1.37% done (average ref count so far 10.2275)
    1.38% done (average ref count so far 10.3378)
    1.39% done (average ref count so far 10.4718)
    1.4% done (average ref count so far 10.5841)
    1.41% done (average ref count so far 10.7390)
    1.42% done (average ref count so far 10.8826)
    1.43% done (average ref count so far 10.9919)
    1.44% done (average ref count so far 11.0934)
    1.45% done (average ref count so far 11.2180)
    1.46% done (average ref count so far 11.3697)
    1.47% done (average ref count so far 11.4235)
    1.48% done (average ref count so far 11.5600)
    1.49% done (average ref count so far 11.6864)
    1.5% done (average ref count so far 11.8598)
    ...
    98.51% done (average ref count so far 11.5540)
    98.52% done (average ref count so far 11.5533)
    98.53% done (average ref count so far 11.5522)
    98.54% done (average ref count so far 11.5521)
    98.55% done (average ref count so far 11.5511)
    98.56% done (average ref count so far 11.5499)
    98.57% done (average ref count so far 11.5490)
    98.58% done (average ref count so far 11.5481)
    98.59% done (average ref count so far 11.5470)
    98.6% done (average ref count so far 11.5462)
    98.61% done (average ref count so far 11.5451)
    98.62% done (average ref count so far 11.5441)
    98.63% done (average ref count so far 11.5429)
    98.64% done (average ref count so far 11.5417)
    98.65% done (average ref count so far 11.5406)
    98.66% done (average ref count so far 11.5394)
    98.67% done (average ref count so far 11.5382)
    98.68% done (average ref count so far 11.5371)
    98.69% done (average ref count so far 11.5359)
    98.7% done (average ref count so far 11.5347)
    98.71% done (average ref count so far 11.5336)
    98.72% done (average ref count so far 11.5324)



```python
print('Average references count for {} works: {:.4f}'.format(count, total/count))
```

    Average references count for 98728842 works: 11.5320


The population average of number of references, as reported by "references-count" field, is 11.53.

### Sample distribution

Let's play with sampling now and see whether (and how well) we can estimate the population average without processing the entire dataset. We will randomly choose a sample of size 50 from our dataset and calculate the number of references for every element in the sample. This 50-point distribution is called a **sample distribution**.


```python
def get_sample_distribution(size, stat_fun):
    sample = []
    while size > 100:
        sample.extend(works.sample(100))
        size = size - 100
    sample.extend(works.sample(size))
    return [stat_fun(s) for s in sample]

sample = get_sample_distribution(50, ref_count)
" ".join([str(s) for s in sample])
```




    '22 17 17 12 0 1 0 0 0 0 0 0 11 7 0 0 0 29 0 20 5 0 35 0 0 53 32 0 0 0 9 28 0 0 15 0 0 0 0 33 4 35 0 0 0 0 0 23 0 0'



We can now calculate the sample average and use this number as the estimate of the population average.


```python
mean(sample)
```




    8.16



Obviously, this is not the real population average, only the estimate. How close is it to the population average?

In this case we know the answer because I calculated the real population average, but usually we have only the sample and the sample average. Of course, we cannot know where our sampled data points are in the overall population. It is possible that, just by chance, we sampled 50 data points with the highest number of references. Such a sample obviously wouldn't give a good estimate of the population average. On the other hand, we could have drawn a sample with the average very close to the population average. This uncertainty related to sampling randomness can be captured by confidence intervals. Intuitively, confidence intervals let us control the amount of uncertainty related to sampling.

Confidence intervals work as follows. We choose the confidence level (a number between 0 and 1). The confidence level roughly means "how certain we want to be about the estimation". Based on the chosen confidence level and sample size we then calculate the confidence interval. Confidence interval is the range, in which we expect the true population average to be. Sample average is always in the middle of that range, and the range has the form (sample average - something, sample average + something).


```python
def confidence_interval(sample, confidence_level):
    return st.t.interval(confidence_level, len(sample)-1, loc=mean(sample), scale=st.sem(sample))

ci = confidence_interval(sample, .95)
ci
```




    (4.456590965585367, 11.863409034414634)



This confidence interval is interpreted as follows: we are 95% sure that the average number of references in the population is within the confidence interval. We will never be 100% using sampling, but this is a decent way to control uncertainty.

What happens if we vary the required confidence level?


```python
for cl in [0.7, 0.9, 0.95, 0.99]:
    ci = confidence_interval(sample, cl)
    print('Based on the sample of size {}, we are {}% sure that the population average is in the range {:.4f}-{:.4f} (estimate {:.4f})'.
          format(len(sample), 100 * cl, ci[0], ci[1], mean(sample)))
```

    Based on the sample of size 50, we are 70.0% sure that the population average is in the range 6.2295-10.0905 (estimate 8.1600)
    Based on the sample of size 50, we are 90.0% sure that the population average is in the range 5.0703-11.2497 (estimate 8.1600)
    Based on the sample of size 50, we are 95.0% sure that the population average is in the range 4.4566-11.8634 (estimate 8.1600)
    Based on the sample of size 50, we are 99.0% sure that the population average is in the range 3.2212-13.0988 (estimate 8.1600)


The more confident we want to be about the range, the wider we have to make it. This should make intuitive sense.

What if we vary the sample size?


```python
cl = 0.95
for size in [25, 50, 100, 200, 400, 800]:
    sample = get_sample_distribution(size, ref_count)
    ci = confidence_interval(sample, cl)
    print('Based on the sample of size {}, we are {}% sure that the population average is in the range {:.4f}-{:.4f} (estimate {:.4f})'.
          format(len(sample), 100 * cl, ci[0], ci[1], mean(sample)))
```

    Based on the sample of size 25, we are 95.0% sure that the population average is in the range 1.2660-29.0540 (estimate 15.1600)
    Based on the sample of size 50, we are 95.0% sure that the population average is in the range 4.9659-19.3941 (estimate 12.1800)
    Based on the sample of size 100, we are 95.0% sure that the population average is in the range 9.6736-19.4264 (estimate 14.5500)
    Based on the sample of size 200, we are 95.0% sure that the population average is in the range 9.0268-26.6232 (estimate 17.8250)
    Based on the sample of size 400, we are 95.0% sure that the population average is in the range 9.1616-13.1684 (estimate 11.1650)
    Based on the sample of size 800, we are 95.0% sure that the population average is in the range 9.4240-13.0035 (estimate 11.2137)


It seems that the larger the sample, the smaller the interval. This also makes intuitive sense. Consider the edge cases. If we randomly choose a sample of size 1, the sample average (in this case simply the number of references of the chosen metadata record) will vary a lot, depending on the random choice. On the other hand, we can choose "randomly" a sample of size equal to the size of the entire dataset, and in this case the estimate will be identical to the true population average.

### Sampling distribution

So intuitively everything seems to work. But where does this magic interval actually come from? It is calculated by the theoretical analysis of the sampling distribution (not to be confused with sample distribution):
  * **sample distribution** is when we collect one sample of size k and calculate our statistic for every element in the sample. It is a distribution of k values of the statistic value in the sample.
  * **sampling distribution** is when we independently collect n samples, each of size k, and calculate the sample average for each sample. It is the distribution of n sample averages.

Note that choosing randomly one sample of size k and calculating the sample average is equivalent to choosing randomly one value from the sampling distribution containing all possible samples of size k. [Central Limit Theorem](https://en.wikipedia.org/wiki/Central_limit_theorem) tells us that sampling distribution is approximately normal with the mean equal to the population mean. Of course, we do not know where in the sampling distribution our chosen sample average lies. Maybe we were lucky and our sample average is close to the middle of the sampling distribution, meaning that sample average is close to the population average. But it is also possible that our sample average is in the tail of the sampling distribution, far from the population average.

Now let's assume we have decided on the confidence level 95%. We can say that we are 95% sure that our sample average lies within the middle 95% of the sampling distribution, that is within 2 standard deviations from the mean. Central Limit Theorem lets us calculate this standard deviation, which gives the upper bound on the distance from our sample mean to the mean of the sampling distribution. Since we know the distance, but not the direction, we obtain a confidence interval in the form (sample mean - 2 * stdev, sample mean + 2 * stdev). Different values of confidence level will give us different distances, but the principle remains the same.

Let's now visualize the sampling distribution for some specific cases. We will generate histograms of sampling distributions for all combinations of n samples of size k, where n and k are the elements of the set {25, 50, 100, 200, 400}.


```python
def get_sampling_distribution(sample_size, stat_fun, samples):
    return [mean(get_sample_distribution(sample_size, stat_fun)) for sample in range(samples)]
```


```python
sizes = [25, 50, 100, 200, 400]
l = len(sizes)
sampling_means = {s: {d : [] for d in sizes} for s in sizes}
means = pd.DataFrame(numpy.zeros((l, l)), index=sizes, columns=sizes)
stdevs = pd.DataFrame(numpy.zeros((l, l)), index=sizes, columns=sizes)
```


```python
for sample_size in sizes:
    for samples in sizes:
        print('{} samples of size {} each'.format(samples, sample_size))
        sampling_means[sample_size][samples] = get_sampling_distribution(sample_size, ref_count, samples)
        means.at[sample_size, samples] = mean(sampling_means[sample_size][samples ])
        stdevs.at[sample_size, samples] = stdev(sampling_means[sample_size][samples])
```

    25 samples of size 25 each
    50 samples of size 25 each
    100 samples of size 25 each
    200 samples of size 25 each
    400 samples of size 25 each
    25 samples of size 50 each
    50 samples of size 50 each
    100 samples of size 50 each
    200 samples of size 50 each
    400 samples of size 50 each
    25 samples of size 100 each
    50 samples of size 100 each
    100 samples of size 100 each
    200 samples of size 100 each
    400 samples of size 100 each
    25 samples of size 200 each
    50 samples of size 200 each
    100 samples of size 200 each
    200 samples of size 200 each
    400 samples of size 200 each
    25 samples of size 400 each
    50 samples of size 400 each
    100 samples of size 400 each
    200 samples of size 400 each
    400 samples of size 400 each


Let's look first at the means of the sampling distributions for all combinations of n and k.


```python
means
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>25</th>
      <th>50</th>
      <th>100</th>
      <th>200</th>
      <th>400</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>25</th>
      <td>10.4928</td>
      <td>10.94000</td>
      <td>12.064800</td>
      <td>11.495000</td>
      <td>11.443800</td>
    </tr>
    <tr>
      <th>50</th>
      <td>12.7104</td>
      <td>11.20200</td>
      <td>11.859200</td>
      <td>12.632700</td>
      <td>11.911800</td>
    </tr>
    <tr>
      <th>100</th>
      <td>12.4476</td>
      <td>11.65020</td>
      <td>11.597800</td>
      <td>11.821650</td>
      <td>11.636300</td>
    </tr>
    <tr>
      <th>200</th>
      <td>12.1348</td>
      <td>12.37760</td>
      <td>11.762250</td>
      <td>11.898500</td>
      <td>11.787175</td>
    </tr>
    <tr>
      <th>400</th>
      <td>11.4893</td>
      <td>11.54785</td>
      <td>11.535375</td>
      <td>11.590475</td>
      <td>11.659975</td>
    </tr>
  </tbody>
</table>
</div>



They seem fairly close to the true population average, perhaps with some outliers. We can also observe that the larger the sample size, the closer we get to the population average.

Now let's see the standard deviations.


```python
stdevs
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>25</th>
      <th>50</th>
      <th>100</th>
      <th>200</th>
      <th>400</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>25</th>
      <td>5.004901</td>
      <td>3.539669</td>
      <td>4.629838</td>
      <td>5.657129</td>
      <td>5.072286</td>
    </tr>
    <tr>
      <th>50</th>
      <td>7.163682</td>
      <td>3.288074</td>
      <td>3.301025</td>
      <td>4.081776</td>
      <td>3.796529</td>
    </tr>
    <tr>
      <th>100</th>
      <td>2.878831</td>
      <td>2.449494</td>
      <td>3.063716</td>
      <td>2.627449</td>
      <td>2.560995</td>
    </tr>
    <tr>
      <th>200</th>
      <td>2.880716</td>
      <td>3.180476</td>
      <td>2.324988</td>
      <td>2.208855</td>
      <td>1.871698</td>
    </tr>
    <tr>
      <th>400</th>
      <td>1.175269</td>
      <td>1.450241</td>
      <td>1.282519</td>
      <td>1.414438</td>
      <td>1.547873</td>
    </tr>
  </tbody>
</table>
</div>



The standard deviation of the sampling distribution depends heavily on the sample size. The larger the size, the lower the standard deviation. This confirms the previous observation: the larger the sample size, the narrower the confidence interval will be.

Finally, let's plot the histograms of the sampling distributions.


```python
f, axes = plt.subplots(5, 5, sharex=True)
for i in range(5):
    for j in range(5):
        axes[i, j].hist(sampling_means[sizes[i]][sizes[j]])
```


![png](sampling_notes_files/sampling_notes_30_0.png)


The histograms also confirm our observations about the means and standard deviations of the sampling distributions.

It is important to note that this technique works with any kind of statistics, and the distribution of the statistic value in the population doesn't have to be normal. Indeed, the distribution of the number of references is most likely skewed.

## Estimating the average search rank

Let's try a different statistic. It will be the rank of the metadata record in the result list, returned when we perform a metadata search using the record's title (without any modifications). Statistically speaking, the main difference from the number of the references is that the new statistic is much more skewed. Typically in the sample we will have a lot of 1s, and rarely an outlier with a high value. To save time iterating through the results list, I truncate the rank at 100. 100 is also returned if there is not title or if the title is empty.


```python
def search_rank_by_title(work):
    if 'title' not in work:
        return 100
    if not work['title']:
        return 100
    title = work['title'][0]
    if not title:
        return 100
    for i, w in enumerate(works.query(title).sort('relevance')):
        if i > 100:
            return 100
        if w['DOI'] == work['DOI']:
            return i+1
    return 100

sample = get_sample_distribution(100, search_rank_by_title)
print('Example sample distribution: ' + ' '.join([str(s) for s in sample]))

for size in [20, 50, 100, 200, 400, 800, 1600]:
    sample = get_sample_distribution(size, search_rank_by_title)
    ci = confidence_interval(sample, cl)
    print('Based on the sample of size {}, we are {}% sure that the population average is in the range {:.4f}-{:.4f} (estimate {:.4f})'.
          format(len(sample), 100 * cl, ci[0], ci[1], mean(sample)))
```

    Example sample distribution: 1 1 1 1 1 1 1 1 1 100 1 1 1 1 100 3 1 1 1 100 2 1 1 100 1 100 1 3 1 63 1 1 11 1 1 100 1 1 1 100 1 100 2 1 1 1 1 2 5 1 1 9 1 1 1 1 1 100 2 1 46 41 1 21 2 2 1 100 1 1 1 1 1 1 1 1 1 100 1 3 1 1 1 1 1 1 100 1 1 74 1 2 1 100 1 1 1 100 8 1
    Based on the sample of size 20, we are 95.0% sure that the population average is in the range -3.8893-16.7893 (estimate 6.4500)
    Based on the sample of size 50, we are 95.0% sure that the population average is in the range 4.8556-23.3444 (estimate 14.1000)
    Based on the sample of size 100, we are 95.0% sure that the population average is in the range 6.2676-17.3124 (estimate 11.7900)
    Based on the sample of size 200, we are 95.0% sure that the population average is in the range 12.1098-21.9302 (estimate 17.0200)
    Based on the sample of size 400, we are 95.0% sure that the population average is in the range 12.3452-19.0098 (estimate 15.6775)
    Based on the sample of size 800, we are 95.0% sure that the population average is in the range 12.4606-17.0094 (estimate 14.7350)
    Based on the sample of size 1600, we are 95.0% sure that the population average is in the range 12.7942-15.9895 (estimate 14.3919)


Lastly, some important things to remember:
  * (Lack of) certainty. Remember that the confidence level < 1. This means, we are never sure that our confidence interval contains the population average. With the confidence level of 95%, if we chose a sample 100 times, just by chance we would get intervals not containing the population average in approximately 5 cases. If for any reason you need to be 100% sure, just process the entire dataset.
  * Randomness. The sample has to be chosen randomly. So no "first 1000 records from the snapshot". Note how different the partial average numbers of references were from the final number, as I was processing the entire dataset.
  * Sample size. We know already that the larger the sample, the better. As a rule of thumb, using sample sizes < 30 makes the estimates, including the interval, pretty unreliable. The reason is that the standard deviation used for all calculations is obtained from the sample, and it becomes unreliable when the size is small. Also, the more skewed the statistic distribution, the larger sample we need. I used rather small sizes in this notebook, but in general I suggest counting in thousands.
  * Generalization. The sample average can be used as an estimate for the population average, but only the population it was drawn from. This means that if we apply any filters before sampling (which is equivalent to sampling from a subset passing the filter), we can reason only about the filtered subset of the data.
  * Averaging. The whole thing only works with averages (and sums). It doesn't work for other aggregate functions. Note that a proportion of records passing a certain filter can be estimated, if we treat it as an average of 0's (doesn't pass) and 1's (passes).
  * Reproducibility. This is more of an engineering concern. In short, all the analyses we do should be reproducible. In the context of sampling it means, at the very least, that we should record the samples obtained from the API.
