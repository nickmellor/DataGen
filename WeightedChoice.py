import csv
import math


class WeightedChoice:
    """
    Generates a stream of random choices (could be a name, shopping cart item, log entry etc.)
    based on a popularity table. More common choices are returned more frequently.
    """

    class RandomNameException(BaseException):
        pass

    class MissingPopularityException(RandomNameException):
        """missing or malformed popularity field contents"""
        pass

    def __init__(self, filename, name_fld="Name", weightRating_fld="Common5"):
        """populate name lookup table and prepare word_weight weightings"""
        item_list = list(csv.DictReader(open(filename)))
        # self.running_total_fld = "rn_runningTotal"
        self.name_fld = name_fld
        self.popularity_fld = weightRating_fld
        # Weed out rows with blank name field (e.g. empty lines at end of file)
        with open(filename) as f:
            item_list = [k for k in csv.DictReader(f)
                         if k[name_fld].strip(' \t\n\r')]
        self.item = []
        self.weight_ceiling = []
        stack_weight = 0.0
        for choice in item_list:
            # Exponentiate 0-5 score for word_weight
            try:
                word_weight = math.exp(float(choice[self.popularity_fld]))
            except:
                raise self.MissingPopularityException(
                    "Weight should be 0..5 on name {0} in file {1}".format(
                        (choice[name_fld], filename)))
            # a name is matched if it is the first name with cumulative weight > pindrop
            stack_weight += word_weight
            self.item.append(choice)
            self.weight_ceiling.append(stack_weight)
        # total_popularity used later to define range over which to choose a name
        self.stack_weight = stack_weight
