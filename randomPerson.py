import bisect
import csv
import hashlib
import math
import os
import random
import re
from fieldmap import translateIn, translateOut
from birthday import birthday
import yaml

from filelinks import output_file, base_dir


# Todo-- pluggable data generators
# (e.g. generate a file of young women entrepreneurs, a corporation
# employing mainly male building contractors, an Asian state in which there are
# fewer women, or generate families (couples, single or double-parent, 1-5 children etc)

class RandomContactException(BaseException):
    """
    base exception for any exception in the RandomPerson class
    """
    pass


class NameLookupException(RandomContactException):
    """error in name/popularity input file"""
    pass


class WeightedRandomChoice:
    """
    Generates a stream of random choices (could be surname, forename, shopping cart item, log entry etc.)
    based on a popularity table. More common choices are returned more frequently.
    """

    class RandomNameException(BaseException):
        pass

    class MissingPopularityException(RandomNameException):
        """missing or malformed popularity field contents"""
        pass

    def __init__(self, filename, name_fld="Name", weightRating_fld="expweight"):
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
        return self.item[self._select()]

    def _select(self):
        pindrop = random.uniform(0.0, self.stack_weight)
        i = bisect.bisect_left(self.weight_ceiling, pindrop)
        if i != len(self.weight_ceiling):
            return i
        raise ValueError


import fieldmap


class RandomContact:
    """
    generate a contact record with random but believable personal data
    """

    class NegSampleSizeException(RandomContactException):
        """
        Negative or zero sample size passed to .save_csv
        """
        pass

    def __init__(self, lookup_root=os.path.normpath(os.path.join(base_dir(), "lookups"))):
        """
        lookup_root specifies where to find lookup tables
        """
        self.lookup_root = lookup_root
        self.firstlineaddress_fld = "street"
        self.website_fld = "website"
        # separate generators for male and female names means lookup tables can
        # be of different sizes and use different distributions of popularity weighting
        # without skewing the overall numbers of male and female names generated
        self.female_forename_generator = \
            WeightedRandomChoice(self.fp("Forenames_female.csv"), name_fld="forename")
        self.male_forename_generator = \
            WeightedRandomChoice(self.fp("Forenames_male.csv"), name_fld="forename")
        self.surname_generator = \
            WeightedRandomChoice(self.fp("Surnames.csv"), name_fld="surname")
        self.address_generator = self.address(self.fp("Addresses.csv"))
        self.fieldorder = []

    def fp(self, filename):
        """return full path of a filename by prepending root directory"""
        return os.path.join(self.lookup_root, filename)

    def address(self, filename):
        """generator returning a random address"""

        # store field order from original address table--
        # used by output functions
        # TODO-- output fieldorder should probably be rethought
        # Input address data might have nothing in common with
        # output address data order
        fieldorder = next(csv.reader(open(filename)))
        # fieldorder = dict(zip(fieldorder, fieldorder))
        # fieldorder = translateIn(fieldorder)
        self.fieldorder = [r for r in fieldorder if r]
        # load in all addresses for random-access
        addresses = tuple(csv.DictReader(open(filename)))
        # translate all the addresses for processing
        addresses = tuple(translateIn(address) for address in addresses)
        while True:
            yield random.choice(addresses)

    def gendered_name(self):
        """
        generate forenames, surname and sex
        Forenames must match in gender
        e.g. "Sarah Jane" and "Robert James" are okay
        but not "Alice Brett" or "Frank Rose"
        """
        forename_generators = {
            'male': self.male_forename_generator,
            'female': self.female_forename_generator
        }
        while True:
            # Flip between male and female name generators at statistically credible rate
            # see http://en.wikipedia.org/wiki/Sex_ratio (CIA estimate)
            sex = "male" if random.randint(0, 1986) > 986 else "female"
            # Generate same-sex first and middle names
            forename_generator = forename_generators[sex]
            yield {
                "first_name": forename_generator.name(),
                "middle_name": forename_generator.name(),
                "last_name": self.surname_generator.name(),
                "sex": sex
            }

    def person(self):
        """generator returning random but fairly realistic personal data:
        name, sex, address, username, password, birthday, email,
        website etc. Data is modelled on an existing
        address list and name frequency tables, with various fields
        obfuscated for privacy."""
        id = 1
        while True:
            # Generate address info
            person = next(self.address_generator)
            # Disguise address-- change all numbers
            # First randomise numbers in first line of address
            firstline = re.split("(^[0-9]+)", person[self.firstlineaddress_fld])
            # If no numbers in address, leave as is
            if len(firstline) != 1:
                # Replace all numbers with random no in 1..5
                for el in firstline:
                    # every number that isn't a house number (street no, Level, flat etc.) is
                    # replaced by a small number
                    if el.isdigit(): el = str(random.randint(1, 5))
                if firstline[0] == "":
                    # Initial number: choose from larger range for house numbers, including odd and even
                    firstline[1] = str(random.randint(0, 75) * 3 + 1)
            # Write first line back
            person[self.firstlineaddress_fld] = "".join(firstline)
            person["birthday"] = birthday()
            # Override or insert surname and forename info
            person.update(next(self.gendered_name()))
            # Generate fake email addresses, usernames and ids

            # OPTIONS:
            #   - Simple username: unique per run
            # username = "test" + str(id)

            #   - More sophisticated: good uniqueness but still contains first name
            # Removing [:5] or increasing 5 to n
            # gives better uniqueness but less readable usernames
            username = "{name}-{hash}".format(name=person["first_name"],
                    hash=hashlib.md5(repr(person).encode()).hexdigest()[:5])
            # Use username for email as well
            # Email domain name could be more sophisticated...
            person.update({"email": username + "@bendigotraders.org",
                           "username": username,
                           "password": "test"})
            yield person
            id += 1

    def save(self, no_of_people, output_filename, output_filetype='django_yaml_fixture',
        yaml_entity='Customer', id_start=1, id_step=1):
        """compile a list of people and save to a file"""
        if no_of_people <= 0:
            raise self.NegSampleSizeException("Can't generate zero or negative sample sizes! (n = %d)" % (no_of_people))
        with file(output_filename, "wb") as outputfile:
            np = self.person()
            # swallow empty first instance
            dontuse = list(next(np).keys())
            if output_filetype == 'csv':
                # Write heading row in order of original contacts table
                # todo-nm outgoing translations passim
                # print("fieldorder", self.fieldorder)
                field_header = [fieldmap.OUTGOING_TRANSLATION[r]
                                for r
                                in self.fieldorder
                                if fieldmap.OUTGOING_TRANSLATION[r]]
                wtr = csv.DictWriter(outputfile, field_header, extrasaction='ignore')
                wtr.writeheader()
            person_id = id_start
            for i in range(no_of_people):
                if output_filetype == 'csv':
                    p = fieldmap.translateOut(next(np))
                    wtr.writerow(p)
                elif output_filetype == 'django_yaml_fixture':
                    p = fieldmap.translateOut(next(np))
                    # print('map', p)
                    outputfile.write(
                        yaml.dump([{'model': yaml_entity,
                                    'pk': person_id,
                                    'fields': p}
                                   ]
                                  )
                    )
                person_id += id_step


# todo optional primary clave, currently only implemented for YAML fixture

if __name__ == "__main__":
    """
    generate a file, size no_of_people, list some names or dump all generated data to console
    """
    # print(yaml.load(open(r"C:\Users\Nick\Documents\Other\My Python\NameGen\translations.yaml", 'r').read()))
    if True:
        generate_file = False
        # save a file of random people
        if generate_file:
            no_of_people = 50
            RandomContact().save(no_of_people,
                                 output_filename=output_file("testing.csv"),
                                 output_filetype='csv')
            RandomContact().save(no_of_people,
                                 output_filename=output_file("testing.yaml"),
                                 output_filetype='django_yaml_fixture',
                                 yaml_entity='harv2.Customer')
        else:
            # demonstrate producing a stream of people of any length
            new_contact = RandomContact().person()
            justnames = False
            if justnames:
                for i in range(50):
                    p = next(new_contact)
                    print("Here's one...")
                    print("%s, %s %s" % (p["Last Name"].upper(), p["First name"], p["Middle name"]))
            else:
                for i in range(10):
                    p = next(new_contact)
                    print()
                    print("==================================")
                    # print everything generated
                    print()
                    for j in p.items():
                        print("%s: %s" % (j[0], j[1]))
                    print()
