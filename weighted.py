import csv
import math
from random import uniform
from bisect import bisect_left
from exceptions import MissingPopularityException


class WeightedChoice:
    """
    Generates a stream of random weighted choices (could be surname, forename, shopping cart item, log entry etc.)
    based on a popularity table. More common choices are returned more frequently.
    """

    def __init__(self, filename, name_field="Name"):
        """populate name lookup table and prepare word weightings"""
        item_list = list(csv.DictReader(open(filename)))
        self.name_field = name_field
        self.filename = filename
        # Weed out rows with blank name field (e.g. empty lines at end of file)
        with open(self.filename) as f:
            item_list = [item for item in csv.DictReader(f) if item[self.name_field].strip(' \t\n\r')]
        self.items = []
        self.weight_ceiling = []
        running_weight = 0.0
        for item in item_list:
            running_weight += self.item_weight(item)
            self.items.append(item)
            self.weight_ceiling.append(running_weight)

    def item_weight(self, item):
        prefix = 'rn_'
        expweight = prefix + 'expweight'
        weight = prefix + 'weight'
        if expweight in item:
            return math.exp(float(item[expweight]))
        elif weight in item:
            return float(item[weight])
        else:
            raise MissingPopularityException(
                "No weight field on name {0} in file {1}".format(
                    (item[self.name_field], self.filename)))

    def name(self):
        """
        returns a random name with frequency based on a popularity
        rating held in two files, one for male, one for female
        e.g. for male forenames, "John" will be emitted often,
        "Bartholomew" rarely
        """
        return self.items[self._select()][self.name_field]

    def _select(self):
        pindrop = uniform(0.0, self.weight_ceiling[-1])
        i = bisect_left(self.weight_ceiling, pindrop)
        if i != len(self.weight_ceiling):
            return i
        raise ValueError
