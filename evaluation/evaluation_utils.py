import utils.data_format_keys as dfk

from statistics import mean


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

    def __get_fraction(self, category):
        return self.results[category] / self.total

    def get_fraction_correct_link(self):
        return self.__get_fraction(self, dfk.EVAL_CORRECT_LINK)

    def get_fraction_correct_no_link(self):
        return self.__get_fraction(self, dfk.EVAL_CORRECT_NO_LINK)

    def get_fraction_incorrect_link(self):
        return self.__get_fraction(self, dfk.EVAL_INCORRECT_LINK)

    def get_fraction_incorrect_exists(self):
        return self.__get_fraction(self, dfk.EVAL_INCORRECT_EXISTS)

    def get_fraction_incorrect_missing(self):
        return self.__get_fraction(self, dfk.EVAL_INCORRECT_MISSING)

    def get_accuracy(self):
        return (self.results[dfk.EVAL_CORRECT_LINK] +
                self.results[dfk.EVAL_CORRECT_NO_LINK]) / self.total

    def print_summary(self):
        print('Reference-based metrics:')
        print('  Accuracy: {:.4f}'.format(self.get_accuracy()))
        print('  Fractions of references:')
        for category in [dfk.EVAL_CORRECT_LINK, dfk.EVAL_CORRECT_NO_LINK,
                         dfk.EVAL_INCORRECT_LINK, dfk.EVAL_INCORRECT_EXISTS,
                         dfk.EVAL_INCORRECT_MISSING]:
            print('    - {}: {:.4f} ({})'.format(category,
                                                 self.__get_fraction(category),
                                                 self.results[category]))


class LinkMetricsResults:

    def __init__(self, dataset, split_by_doc=True):
        self.correct = \
            len([d for d in dataset
                 if d[dfk.DATASET_DOI_GT] == d[dfk.DATASET_DOI_TEST]
                 and d[dfk.DATASET_DOI_GT] is not None])
        self.gt = len([d for d in dataset
                       if d[dfk.DATASET_DOI_GT] is not None])
        self.test = len([d for d in dataset
                         if d[dfk.DATASET_DOI_TEST] is not None])
        self.results_by_doc = {}
        if split_by_doc:
            dataset_by_doc = split_by_target_doc(dataset)
            self.results_by_doc = {doc: LinkMetricsResults(d, False)
                                   for doc, d in dataset_by_doc.items()}

    def get_precision(self):
        if self.test == 0:
            return 1.
        return self.correct / self.test

    def get_recall(self):
        if self.gt == 0:
            return 1.
        return self.correct / self.gt

    def get_f1(self):
        precision = self.get_precision()
        recall = self.get_recall()
        if precision == 0 or recall == 0:
            return 0.
        return 2 * precision * recall / (precision + recall)

    def __get_fun_by_doc(self, fun):
        return {doc: fun(r) for doc, r in self.results_by_doc.items()}

    def get_precision_by_doc(self):
        return self.__get_fun_by_doc(lambda x: x.get_precision())

    def get_recall_by_doc(self):
        return self.__get_fun_by_doc(lambda x: x.get_recall())

    def get_f1_by_doc(self):
        return self.__get_fun_by_doc(lambda x: x.get_f1())

    def __get_average_fun_by_doc(self, fun):
        return mean([fun(r) for r in self.results_by_doc.values()])

    def get_average_precision_by_doc(self):
        return self.__get_average_fun_by_doc(lambda x: x.get_precision())

    def get_average_recall_by_doc(self):
        return self.__get_average_fun_by_doc(lambda x: x.get_recall())

    def get_average_f1_by_doc(self):
        return self.__get_average_fun_by_doc(lambda x: x.get_f1())

    def print_summary(self):
        print('Link-based metrics:')
        print('  Precision: {:.4f}'.format(self.get_precision()))
        print('  Recall: {:.4f}'.format(self.get_recall()))
        print('  F1: {:.4f}'.format(self.get_f1()))
        if self.results_by_doc:
            print('Document-level metrics:')
            print('  Average precision: {:.4f}'
                  .format(self.get_average_precision_by_doc()))
            print('  Average recall: {:.4f}'
                  .format(self.get_average_recall_by_doc()))
            print('  Average F1: {:.4f}'.format(self.get_average_f1_by_doc()))


def split_by_attr(dataset, attr):
    attr_values = set([d[attr] for d in dataset if d[attr] is not None])
    split_dataset = {a: [] for a in attr_values}
    for item in dataset:
        if item[attr] is not None:
            split_dataset[item[attr]].append(item)
    return split_dataset


def split_by_target_doc(dataset):
    split_dataset = split_by_attr(dataset, dfk.DATASET_DOI_GT)
    for item in dataset:
        if item[dfk.DATASET_DOI_TEST] in split_dataset:
            if item not in split_dataset[item[dfk.DATASET_DOI_TEST]]:
                split_dataset[item[dfk.DATASET_DOI_TEST]].append(item)
    return split_dataset
