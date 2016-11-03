import csv
import math


# class WeightedChoice:
#     """
#     Generates a stream of random choices (could be a name, shopping cart item, log entry etc.)
#     based on a popularity table. More common choices are returned more frequently.
#     """
#
#     class RandomNameException(BaseException):
#         pass
#
#     class MissingPopularityException(RandomNameException):
#         """missing or malformed popularity field contents"""
#         pass
#
#     def __init__(self, filename, name_fld="Name", weightRating_fld="Common5"):
#         """populate name lookup table and prepare word_weight weightings"""
#         item_list = list(csv.DictReader(open(filename)))
#         # self.running_total_fld = "rn_runningTotal"
#         self.name_fld = name_fld
#         self.popularity_fld = weightRating_fld
#         # Weed out rows with blank name field (e.g. empty lines at end of file)
#         with open(filename) as f:
#             item_list = [k for k in csv.DictReader(f)
#                          if k[name_fld].strip(' \t\n\r')]
#         self.item = []
#         self.weight_ceiling = []
#         stack_weight = 0.0
#         for choice in item_list:
#             # Exponentiate 0-5 score for word_weight
#             try:
#                 word_weight = math.exp(float(choice[self.popularity_fld]))
#             except:
#                 raise self.MissingPopularityException(
#                     "Weight should be 0..5 on name {0} in file {1}".format(
#                         (choice[name_fld], filename)))
#             # a name is matched if it is the first name with cumulative weight > pindrop
#             stack_weight += word_weight
#             self.item.append(choice)
#             self.weight_ceiling.append(stack_weight)
#         # total_popularity used later to define range over which to choose a name
#         self.stack_weight = stack_weight

class WeightedChoice:
    """
    Generates a stream of random choices (could be surname, forename, shopping cart item, log entry etc.)
    based on a popularity table. More common choices are returned more frequently.
    """

    def __init__(self, filename, name_fld="Name"):
        """populate name lookup table and prepare word weightings"""
        item_list = list(csv.DictReader(open(filename)))
        self.name_fld = name_fld
        self.filename = filename
        # Weed out rows with blank name field (e.g. empty lines at end of file)
        with open(self.filename) as f:
            item_list = [k for k in csv.DictReader(f)
                         if k[name_fld].strip(' \t\n\r')]
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
            raise self.MissingPopularityException(
                "No weight field on name {0} in file {1}".format(
                    (item[self.name_fld], self.filename)))

    def name(self):
        """
        returns a random name with frequency based on a subjective
        popularity rating held in two files, one for male, one for female
        e.g. for male forenames, "John" will be emitted often,
        "Bartholomew" rarely
        """
        return self.all()[self.name_fld]

    def all(self):
        """return name and pass through other information in lookup table"""
        # pick a random item in the popularity interval over all words
        return self.items[self._select()]

    def _select(self):
        pindrop = random.uniform(0.0, self.weight_ceiling[-1])
        i = bisect.bisect_left(self.weight_ceiling, pindrop)
        if i != len(self.weight_ceiling):
            return i
        raise ValueError


