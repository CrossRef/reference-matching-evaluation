# Evaluation framework for reference matching algorithms

This code allows for:

  * generating artificial datasets for reference matching
  * applying reference matching approaches
  * evaluating various reference matching approaches

[Here](https://docs.google.com/document/d/1X0clkjH-HM3DLVPWDgAZgS97Th4slniq28F9o-yd53k) are the notes about reference matching task in general, various ideas for dataset generation and the definitions of useful evaluation metrics.

Before running the scripts, add the code directory path to the environment variable PYTHONPATH.

## Dataset generation

A dataset is generated in several steps:

### Sample extraction

Drawing the sample of documents from the system.

```
dataset/draw_sample.py [-h] [-v] -s SIZE [-f FILTER] [-q QUERY] -o OUTPUT
```

Arguments:

  * **-h** print help
  * **-v** verbose output
  * **-s** sample size
  * **-f** filter to apply before drawing the sample
  * **-q** query to apply before drawing the sample
  * **-o** output file path

### Sample extension

Extending the sample by adding similar documents.

```
dataset/extend_sample.py [-h] [-v] -s SAMPLE -e EXTEND -o OUTPUT
```

Arguments:

  * **-h** print help
  * **-v** verbose output
  * **-s** sample file path
  * **-e** number of similar documets to add for each sample document
  * **-o** output file path

### Generating the dataset

Generating reference strings and the final dataset.

```
dataset/generate_dataset.py [-h] [-v] [-l STYLES] [-a ATTRIBUTES] [-n] -s SAMPLE -o OUTPUT
```

Arguments:

  * **-h** print help
  * **-v** verbose output
  * **-l** comma-separated list of citation styles
  * **-a** comma-separated list of document attributes to keep (useful if we want to calculate the results along the values of those attributes)
  * **-n** set the target DOIs to null
  * **-s** sample file path
  * **-o** output file path

## Reference matching

Match the references from the dataset to target DOIs.

```
matching/match_references.py [-h] [-v] -d DATASET -o OUTPUT
```

Arguments:

  * **-h** print help
  * **-v** verbose output
  * **-d** dataset file path
  * **-o** output file path

The matching algorithm is set by specifying the matcher object in `matching/match_config.py`. The matcher object should implement two methods:

  * description(): returns a string
  * match(reference_string): returns a tuple (matched DOI, matching score)

## Evaluation

Evaluate the reference matching. The results are printed to stdout.

```
evaluation/evaluate.py [-h] [-v] -d DATASET [-s SPLITATTR] [-o OUTPUTDOC] [-p OUTPUTSPLIT]
```

Arguments:

  * **-h** print help
  * **-v** verbose output
  * **-d** dataset file path (matched)
  * **-s** attribute along which the results should be split
  * **-o** output file path for document-level results
  * **-p** output file path for split attribute results

## Additional scripts

### Datasets merging

Merge two or more samples or references datasets into a single file.

```
dataset/merge_datasets.py [-h] [-v] -d DATASETS -o OUTPUT
```

Arguments:

  * **-h** print help
  * **-v** verbose output
  * **-d** comma-separated list of dataset file paths
  * **-o** output file path

### Links export

Export the information about a sample of existing and missing links in the current system.

```
dataset/export_existing_and_new_links.py [-h] [-v] -s SAMPLE [-n REFERENCES] -o OUTPUT
```

Arguments:

  * **-h** print help
  * **-v** verbose output
  * **-s** sample file path
  * **-n** max number of output references
  * **-o** output file path

