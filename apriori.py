"""
implement the Apriori algorithm

tested with python 3.X
"""

import re
from collections import defaultdict
from itertools import combinations, chain
from optparse import OptionParser

import pickle


def parse_file(filename):
    """
    parset the file to get all transactions.
    Translate the binary value of Up/Down to G##_Up/G##_Down.

    Return each line as a single transaction.
    """

    with open(filename, 'r') as f:
        contents = f.readlines()
        f.close()

    _transactions = []
    for line in contents:
        attributes = re.split('\t', line.strip())
        order = 1
        transaction = []
        for attr in attributes[:-1]:
            transaction.append(('G' + str(order) + '_' + attr).upper())
            order += 1
        transaction.append(attributes[-1])
        _transactions.append(transaction)

    return _transactions


def get_subsets(arr):
    """
    get and return all subsets of a string/array/set/list
    """
    return chain(*[combinations(arr, index + 1) for index, item in enumerate(arr)])


def find_one_itemsets(transactions):
    """
    get all elemeents from all transactions.

    return:
        to keep consistant with k-itemsets, each element will form a single set.
        Since no two elements within the same set can be the same, frozenset will be used
        to make each single set immutable.
    """
    _one_itemsets = set()
    for trans in transactions:
        for item in trans:
            _one_itemsets.add(frozenset([item]))
    return _one_itemsets


def get_frequent_itemsets(itemsets, transactions, support, frequent_itemsets_count):
    _itemsets_dict = defaultdict(int)
    _frequent_itemsets = set()

    for item in itemsets:
        for trans in transactions:
            if item.issubset(trans):
                _itemsets_dict[item] += 1
                frequent_itemsets_count[item] += 1

    for item, count in _itemsets_dict.items():
        if count >= support * len(transactions):
            _frequent_itemsets.add(item)

    return _frequent_itemsets


def apriori_gen(frequent_set, length):
    """
    generate candidate k-itemsets from the frequent (k-1)-itemsets
    """
    return set([i.union(j) for i in frequent_set for j in frequent_set if len(i.union(j)) == length])


def all_subsets_are_frequent(itemset, frequent_itemsets):
    """
    """
    length = len(itemset)
    subsets = chain(*[combinations(itemset, length - 1)])
    subsets = map(frozenset, [sub for sub in subsets])
    for sub in subsets:
        if sub not in frequent_itemsets:
            return False
    return True


def additional_candidate_pruning(candidate_itemsets, frequent_itemsets):
    """
    for each candidate k-itemset, check to see whether all its (k-1)-subsets are frequent or not.

    parameters:
        candidate_itemsets:
        frequent_itemsets:

    return:

    """
    return set([item for item in candidate_itemsets if all_subsets_are_frequent(item, frequent_itemsets)])


def apriori(transactions, support, frequent_itemsets, frequent_itemsets_count):
    result = dict()
    one_itemsets = find_one_itemsets(transactions)
    frequent_itemsets_one = get_frequent_itemsets(one_itemsets, transactions, support, frequent_itemsets_count)

    frequenct_current = frequent_itemsets_one

    k = 2
    while frequenct_current != set([]):
        frequent_itemsets[k - 1] = frequenct_current
        result[k - 1] = len(frequenct_current)
        k_plus_one = apriori_gen(frequenct_current, k)
        k_plus_one = additional_candidate_pruning(k_plus_one, frequenct_current)
        frequent_k_plus_one = get_frequent_itemsets(k_plus_one, transactions, support, frequent_itemsets_count)
        frequenct_current = frequent_k_plus_one
        k += 1

    print_apriori_result(result, support)


def print_apriori_result(result, support):
    print("Support is set to be " + str(support * 100) + "%")
    for length, count in result.items():
        print("number of length-" + str(length) + " frequent itensets: " + str(count))


def rule_generation(itemsets, itemsets_count, confidence):
    """
    generate rules from itemsets
    """
    _rules = []
    for key, value in itemsets.items():
        for item in value: # value is a set, whose elements are frozensets
            all_subsets = get_subsets(item)
            all_subsets = map(frozenset, [x for x in all_subsets])
            for sub in all_subsets:
                rest = item.difference(sub)
                if len(rest) == 0:
                    continue
                if float(itemsets_count[item]) / float(itemsets_count[sub]) >= confidence:
                    _rules.append((item, tuple(sub), tuple(rest)))   # rule, body, head

    return _rules


if __name__ == "__main__":
    option_parser = OptionParser()
    option_parser.add_option("-f", dest="input_file", default="associationruletestdata.txt")
    option_parser.add_option("-s", dest="support", default=0.5)
    option_parser.add_option("-c", dest="confidence", default=0.7)
    (options, args) = option_parser.parse_args()

    records = parse_file(options.input_file)

    all_frequent_itemsets = dict()
    all_frequent_itemsets_count = defaultdict(int)
    min_support = float(options.support)
    apriori(records, min_support, all_frequent_itemsets, all_frequent_itemsets_count)

    min_confidence = float(options.confidence)
    rules = rule_generation(all_frequent_itemsets, all_frequent_itemsets_count, min_confidence)
    pickle.dump(rules, open("rules", "wb"))
