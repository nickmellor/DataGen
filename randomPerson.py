__author__ = 'nick'


########################## Random Person Generator ###################################
##########################    by Nick Mellor       ###################################
##########################     Version 1.2 alpha   ###################################
##########################        Mar 2013         ###################################

"""
Random Personal Data Generator
Generates random details of fictitious people by obfuscating an existing
address list and randomly choosing new names and personal characteristics

Includes:
full name, sex, birthdate, address, web address,
email address etc. based on an existing contact list, name popularity data and
basic demographics

Generates CSV file, YAML file (Django fixture) or a continuous stream of people
in Python dictionaries

An ordinary contact list can be dropped into the generator unchanged
to act as model data-- you can use your own address book to generate realistic
contact details. The initial file format is Outlook export CSV but can easily be
modified for other sources

Transformations:

Typically your address database and your target database differ in format. NameGen
can take one set of field names and transform them into another. See fieldmap.py

Obfuscations include:
  - all numbers in first line of address are changed
  - names are randomised (popularity-adjusted)
  - web addresses are decoupled from postal addresses
  - usernames and emails are regenerated
  - birthdays are randomised (realistically)

Performance:
1000+ people per second (2GHz laptop, 200 entries in input address file)

Dependencies:
pyyaml for test framework

Use:
See examples at end of module

Future:
- With the right datafiles, could mix names from different nationalities or demographics
  (e.g. software developers, middle managers, single parents) and/or generate data for other
  purposes such as organisation names, job titles, fruit and vegetable orders etc.
- Obfuscate production databases to protect client privacy

Updates:
Nov 2012-- unit tests, minor refactorings and code commenting
Jan 2013-- began work on output transformations (selecting and renaming of data
           fields
Mar 2013-- input and output transformations in place


"""

import yaml
import math
import os
import csv
import re
import hashlib
import random
import bisect
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

    def __init__(self, filename, name_fld="Name", weightRating_fld="Common5"):
        """populate name lookup table and prepare word_weight weightings"""
        item_list = list(csv.DictReader(open(filename)))
        #self.running_total_fld = "rn_runningTotal"
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

    def __init__(self, lookup_root=os.path.join(base_dir(), "lookups")):
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
            WeightedRandomChoice(self.fp("Forenames_female.csv"), name_fld="Forename")
        self.male_forename_generator = \
            WeightedRandomChoice(self.fp("Forenames_male.csv"), name_fld="Forename")
        self.surname_generator = \
            WeightedRandomChoice(self.fp("Surnames.csv"), name_fld="Surname")
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
        fieldorder = csv.reader(open(filename)).next()
        fieldorder = dict(zip(fieldorder, fieldorder))
        fieldorder = fieldmap.translateIn(fieldorder)
        self.fieldorder = [r for r in fieldorder if r]
        # load in all addresses for random-access
        addresses = tuple(csv.DictReader(open(filename)))
        # translate all the addresses for processing
        addresses = tuple(fieldmap.translateIn(address) for address in addresses)
        while True:
            yield random.choice(addresses)

    def gendered_name(self):
        """
        generate forenames, surname and sex
        Forenames must match in gender
        e.g. "Sarah Jane" and "Robert James" are okay
        but not "Alice Brett" or "Frank Rose"
        """
        while True:
            # Flip between male and female name generators at statistically credible rate
            # see http://en.wikipedia.org/wiki/Sex_ratio
            # (using CIA estimate)
            sex = "male" if random.randint(0,1986) > 986 else "female"
            # first name and middle name must be of same sex
            if sex == "female":
                forename_generator = self.female_forename_generator
            else:
                forename_generator = self.male_forename_generator

            yield  {
                "first_name" : forename_generator.name(),
                "middle_name" : forename_generator.name(),
                "last_name" : self.surname_generator.name(),
                "sex" : sex
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
            person = self.address_generator.next()
            # Disguise address-- change all numbers
            # First randomise numbers in first line of address
            firstline = re.split("(^[0-9]+)", person[self.firstlineaddress_fld])
            # If no numbers in address, leave as is
            if len(firstline) != 1:
                # Replace all numbers with random no in 1..5
                for el in firstline:
                    # every number that isn't a house number (street no, Level, flat etc.) is
                    # replaced by a small number
                    if el.isdigit(): el = str(random.randint(1,5))
                if firstline[0] == "":
                    # Initial number: choose from larger range for house numbers, including odd and even
                    firstline[1] = str(random.randint(0,75) * 3 + 1)
            # Write first line back
            person[self.firstlineaddress_fld] = "".join(firstline)
            person["birthday"] = self.birthday()
            # Override or insert surname and forename info
            person.update(self.gendered_name().next())
            # Generate fake email addresses, usernames and ids

            # OPTIONS:
            #   - Simple username: unique per run
            #username = "test" + str(id)

            #   - More sophisticated: good uniqueness but still contains first name
            # Removing [:5] or increasing 5 to n
            # gives better uniqueness but less readable usernames
            username = person["first_name"] + "-" \
                       + hashlib.md5(repr(person)).hexdigest()[:5]
            # Use username for email as well
            # Email domain name could be more sophisticated...
            person.update({"email" : username + "@bendigotraders.org",
                           "username" : username,
                           "password" : "test"})
            yield person
            id += 1
            
    def birthday(self):
        """Return random birthdays (string, dd/mm/yyyy). Attempts to distribute birthdays realistically."""
        # Normal Distribution by default
        # See http://en.wikipedia.org/wiki/Median_age for population models
        # TODO-- sex differences
        birthyear = int(random.normalvariate(1960, 15))
        birthmonth = random.randint(1, 12)
        monthlen = (31,28,31,30,31,30,31,31,30,31,30,31)
        lastdayofmonth = monthlen[birthmonth - 1]
        # take leap year into account: allow 29 days in some Febs
        if (birthmonth == 2
         and birthyear % 4 == 0
         and (birthyear % 100 != 0 or birthyear % 400 == 0)):
            lastdayofmonth = 29
        # choose day of month
        birthday = int(random.uniform(1.0, 31.0) *
                       (float(lastdayofmonth) / 31) + 1.0)
        return "%d/%d/%d" % (birthday, birthmonth, birthyear)

    def save(self,
             no_of_people,
             output_filename,
             output_filetype='django_yaml_fixture',
             yaml_entity='Customer',
             id_start=1,
             id_step=1):
        """compile a list of people and save to a file"""
        if no_of_people <= 0:
            raise self.NegSampleSizeException(\
                "Can't generate zero or negative sample sizes! (n = %d)" % (no_of_people))
        with file(output_filename, "wb") as outputfile:
            np = self.person()
            # swallow empty first instance
            dontuse = list(np.next().keys())
            if output_filetype == 'csv':
                # Write heading row in order of original contacts table
                # todo-nm outgoing translations passim
                #print("fieldorder", self.fieldorder)
                field_header = [fieldmap.OUTGOING_TRANSLATION[r]
                                for r
                                in self.fieldorder
                                if fieldmap.OUTGOING_TRANSLATION[r]]
                wtr = csv.DictWriter(outputfile, field_header, extrasaction='ignore')
                wtr.writeheader()
            person_id = id_start
            for i in range(no_of_people):
                if output_filetype == 'csv':
                    p = fieldmap.translateOut(np.next())
                    wtr.writerow(p)
                elif output_filetype == 'django_yaml_fixture':
                    p = fieldmap.translateOut(np.next())
                    #print('map', p)
                    outputfile.write(
                        yaml.dump([{ 'model' : yaml_entity,
                                        'pk' : person_id,
                                    'fields' : p}
                                  ]
                        )
                    )
                person_id += id_step

# todo optional primary key, currently only implemented for YAML fixture

if __name__ == "__main__":
    """
    generate a file, size no_of_people, list some names or dump all generated data to console
    """
    generate_file = True
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
        justnames = True
        if justnames:
            for i in range(50):
                p = new_contact.next()
                print "%s, %s %s" % (p["Last Name"].upper(), p["First name"], p["Middle name"])
        else:
            for i in range(10):
                p = new_contact.next()
                print
                print "=================================="
                # print everything generated
                print
                for j in p.items():
                    print "%s: %s" % (j[0], j[1])
                print
