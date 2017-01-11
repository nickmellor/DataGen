from weighted import WeightedChoice
from filelinks import lookup_file
from random import randint


class NameBuilder:

    """
        separate generators for male and female names means lookup tables can
        be of different sizes and use different distributions of popularity weighting
        without skewing the overall numbers of male and female names generated
    """

    def __init__(self):
        self.female_forename = WeightedChoice(lookup_file("female_forenames.csv"), name_field="forename")
        self.male_forename = WeightedChoice(lookup_file("male_forenames.csv"), name_field="forename")
        self.surname_generator = WeightedChoice(lookup_file("surnames.csv"), name_field="surname")

    def gendered_name(self):
        """
        generate forenames, surname and gender
        Forenames must match in gender
        e.g. "Sarah Jane" and "Robert James" are okay
        but not "Alice Brett" or "Brian Rose"
        """
        while True:
            # Flip between male and female name generators at statistically credible rate
            # see http://en.wikipedia.org/wiki/Sex_ratio (CIA estimate)
            sex_female = randint(0, 1986) > 986
            # Generate same-sex first and middle names
            forename_generator = self.female_forename if sex_female else self.male_forename
            yield {
                "first_name": forename_generator.name(),
                "middle_name": forename_generator.name(),
                "last_name": self.surname_generator.name(),
                "sex": 'female' if sex_female else 'male',
                'sex_female': sex_female,
                'sex_male': not sex_female
            }


if __name__ == '__main__':
    n = NameBuilder()
    for i in range(5):
        print(next(n.gendered_name()))
