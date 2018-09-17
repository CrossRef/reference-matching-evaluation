import utils.data_format_keys as dfk


class ReferenceMetricsResults:

    def __init__(self, dataset):
        self.total = len(dataset)

        self.results = {}

        self.results[dfk.EVAL_CORRECT_LINK] = \
            len([d for d in dataset
                 if d[dfk.DATASET_DOI_GT] == d[dfk.DATASET_DOI_TEST]
                 and d[dfk.DATASET_DOI_GT] is not None])
        self.results[dfk.EVAL_CORRECT_NO_LINK] = \
            len([d for d in dataset
                 if d[dfk.DATASET_DOI_GT] == d[dfk.DATASET_DOI_TEST]
                 and d[dfk.DATASET_DOI_GT] is None])
        self.results[dfk.EVAL_INCORRECT_LINK] = \
            len([d for d in dataset
                 if d[dfk.DATASET_DOI_GT] != d[dfk.DATASET_DOI_TEST]
                 and d[dfk.DATASET_DOI_GT] is not None
                 and d[dfk.DATASET_DOI_TEST] is not None])
        self.results[dfk.EVAL_INCORRECT_EXISTS] = \
            len([d for d in dataset
                 if d[dfk.DATASET_DOI_GT] != d[dfk.DATASET_DOI_TEST]
                 and d[dfk.DATASET_DOI_GT] is None])
        self.results[dfk.EVAL_INCORRECT_MISSING] = \
            len([d for d in dataset
                 if d[dfk.DATASET_DOI_GT] != d[dfk.DATASET_DOI_TEST]
                 and d[dfk.DATASET_DOI_TEST] is None])

    def get_fraction(self, category):
        return self.results[category] / self.total

    def get_fraction_correct_link(self):
        return self.get_fraction(self, dfk.EVAL_CORRECT_LINK)

    def get_fraction_correct_no_link(self):
        return self.get_fraction(self, dfk.EVAL_CORRECT_NO_LINK)

    def get_fraction_incorrect_link(self):
        return self.get_fraction(self, dfk.EVAL_INCORRECT_LINK)

    def get_fraction_incorrect_exists(self):
        return self.get_fraction(self, dfk.EVAL_INCORRECT_EXISTS)

    def get_fraction_incorrect_missing(self):
        return self.get_fraction(self, dfk.EVAL_INCORRECT_MISSING)

    def get_accuracy(self):
        return (self.results[dfk.EVAL_CORRECT_LINK] +
                self.results[dfk.EVAL_CORRECT_NO_LINK]) / self.total


class LinkMetricsResults:

    def __init__(self, dataset):
        self.correct = \
            len([d for d in dataset
                 if d[dfk.DATASET_DOI_GT] == d[dfk.DATASET_DOI_TEST]
                 and d[dfk.DATASET_DOI_GT] is not None])
        self.gt = len([d for d in dataset
                       if d[dfk.DATASET_DOI_GT] is not None])
        self.test = len([d for d in dataset
                         if d[dfk.DATASET_DOI_TEST] is not None])

    def get_precision(self):
        return self.correct / self.test

    def get_recall(self):
        return self.correct / self.gt

    def get_f1(self):
        return 2 / (1 / self.get_precision() + 1 / self.get_recall())
