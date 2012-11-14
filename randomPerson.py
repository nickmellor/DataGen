__author__ = 'nick'
######################### Random Person Generator ###################################
#########################    by Nick Mellor       ###################################
#########################     Version 1.0         ###################################
#########################      June 2009          ###################################
"""Random Personal Data Generator
Generates random details of fictitious people (for testing purposes?)

Includes:
full name, sex, birthdate, address, web address,
email address etc. based on an existing contact list, name popularity data and
basic demographics

Generates either a CSV file or a continuous stream of realistic but random personal data

Random data is based on obfuscated real-world addresses

An ordinary contact list can be dropped into the generator unchanged
to act as model data-- you can use your own address book to generate realistic
contact details. The initial file format is Outlook export CSV but can easily be
modified for other sources

Obfuscations include:
  - all numbers in first line of address are changed
  - names are randomised (popularity-adjusted)
  - web addresses are decoupled from postal addresses
  - usernames and emails are regenerated
  - birthdays are randomised (realistically)

Performance:
Not bad. 2000+ people per second (2GHz laptop, 200 entries in address file)

Use:
See examples at end of module

Future (Nov 2012):
- With the right datafiles, could mix names from different nationalities or demographics
  (e.g. software developers, middle managers, single parents) and/or generate data for other
  purposes such as organisation names, job titles, fruit and vegetable orders etc.
- remove string literals from code (e.g. "First name")
- Better unit testing:
    check forenames and middle names match

Updates:
Nov 2012-- minor refactorings and code commenting
"""

from math import exp
import math
import os
import csv
import re
import hashlib
import random
from filelinks import lookup_file, output_file, base_dir

class RandomPersonException(BaseException):
    """
    any exception in the RandomPerson class
    """
    pass

class NameLookupException(RandomPersonException):
    """error in name/popularity input file"""
    pass

class RandomName:
    """
    Generates a stream of random names (could be surname, forename, middle name, organisation etc.)
    based on a name popularity lookup table.
    More common names are returned exponentially more frequently.
    Common5 field contains zero for uncommon name to 5 for very common
    """

    class RandomNameException(BaseException): pass
    class MissingPopularityException(RandomNameException): pass

    def __init__(self, filename, name_fld="Name", namepopularity_fld="Common5"):
        """populate name lookup table and prepare popularity weightings"""
        self.filename = filename
        self.name_fld = name_fld
        namelist = list(csv.DictReader(open(filename)))
        self.running_total_fld = "rn_runningTotal"
        self.popularity_fld = namepopularity_fld
        running_total = 0.0
        # Weed out rows with blank name field (e.g. empty lines at end of file)
        self.namelist = [k for k in namelist if k[name_fld].strip(' \t\n\r')]
        for name_candidate in self.namelist:
            # Exponentiate 0-5 score for popularity
            try:
                popularity = math.exp(float(name_candidate[self.popularity_fld]))
            except:
                raise self.MissingPopularityException(\
                    "Popularity should be 0..5 on name %s in file %s" % \
                    (name_candidate[self.name_fld], self.filename))
            # running_total is value that selects this name
            # a name that matches is the first (in a sorted list) whose running_total
            # is greater than a random number over an interval spanning all names
            # Names span a part of the whole interval proportional to their popularity
            running_total += popularity
            name_candidate[self.running_total_fld] = running_total
        # total_popularity used later to define range over which to choose a name
        self.total_popularity = running_total

    def name(self):
        """
        returns a random name with frequency based on a subjective
        popularity rating e.g. for male forenames, "John" will be emitted often,
        "Bartholomew" very rarely
        """
        # pick a random spot in the popularity interval over all words
        pindrop = random.uniform(0.0, self.total_popularity)
        # which word did that spot fall on? (Linear search)
        for name_candidate in self.namelist:
            if pindrop <= name_candidate[self.running_total_fld]:
                return name_candidate[self.name_fld].capitalize()
        # it's the last entry if none matched previously
        return self.namelist[-1][self.name_fld]


class RandomPerson:
    """
    generate a "person" record with random but believable personal data
    """
    class NegSampleSizeException(RandomPersonException):
        """
        Negative sample size passed to .save_csv
        """
        pass

    def __init__(self, lookup_root=os.path.join(base_dir(), "lookups")):
        """
        lookup_root specifies where to find lookup tables
        """
        self.lookup_root = lookup_root
        self.firstlineaddress_fld = "Street"
        self.website_fld = "Website"
        # separate generators for male and female names means lookup tables can
        # be of different sizes and use different distributions of popularity weighting
        # without skewing the overall numbers of male and female names generated
        self.female_forename_generator = \
            RandomName(self.fp("Forenames_female.csv"), name_fld="Forename")
        self.male_forename_generator = \
            RandomName(self.fp("Forenames_male.csv"), name_fld="Forename")
        self.surname_generator = \
            RandomName(self.fp("Surnames.csv"), name_fld="Surname")
        self.address_generator = self.address(self.fp("Addresses.csv"))
        self.fieldorder = []

    def fp(self, filename):
        """return full path of a filename by prepending root directory"""
        return os.path.join(self.lookup_root, filename)

    def address(self, filename):
        """generator returning a random address"""

        # store field order from original address table--
        # used by output functions
        self.fieldorder = csv.reader(open(filename)).next()
        # load in whole list for speed
        addresses = list(csv.DictReader(open(filename)))
        while True:
            k = dict.copy(random.choice(addresses))
            k[self.website_fld] = \
                        random.choice(addresses)[self.website_fld]
            yield k

    def name_and_sex(self):
        """
        generate forenames, surname and sex (forenames clearly depend on sex)
        """
        while True:
            # Flip between male and female name generators at statistically credible rate
            # see http://en.wikipedia.org/wiki/Sex_ratio
            sex = "male" if random.randint(0,1986) > 986 else "female"
            # first name and middle name must be of same sex
            if sex == "female":
                forename_generator = self.female_forename_generator
            else:
                forename_generator = self.male_forename_generator
            yield  {
                "First name" : forename_generator.name(),
                "Middle name" : forename_generator.name(),
                "Last Name" : self.surname_generator.name(),
                "Sex" : sex
            }

    def person(self):
        """generator returning random but realistic personal data:
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
            # Birthday
            person["Birthday"] = self.birthday()
            # Override (if already present in address data) or insert surname and forename info
            person.update(self.name_and_sex().next())
            # Generate fake email addresses, usernames and ids

            # Simple username: unique per run
            #username = "test" + str(id)

            # More sophisticated: good uniqueness but still contains first name
            # Removing [:5] or increasing to [:n]
            # gives better uniqueness but less readable usernames
            username = person["First name"] + "-" \
                       + hashlib.md5(repr(person)).hexdigest()[:5]
            # Use username for email as well
            # Email domain name could be more sophisticated...
            person.update({"Email" : username + "@bendigotraders.org",
                           "username" : username,
                           "password" : "test"})
            yield person
            id += 1
            
    def birthday(self):
        """Return random birthdays (string, dd/mm/yyyy). Attempts to distribute birthdays realistically."""
        # Normal Distribution by default
        # See http://en.wikipedia.org/wiki/Median_age for population models
        birthyear = int(random.normalvariate(1960, 15))
        birthmonth = random.randint(1, 12)
        monthlen = (31,28,31,30,31,30,31,31,30,31,30,31)
        lastdayofmonth = monthlen[birthmonth - 1]
        # take leap year into account: allow 29 days in some Febs
        if (birthmonth == 2
         and birthyear%4 == 0
         and (birthyear%100 != 0 or birthyear%400 == 0)):
            lastdayofmonth = 29
        # choose day of month
        birthday = int(random.uniform(1.0, 31.0) * (float(lastdayofmonth) / 31) + 1.0)
        return "%d/%d/%d" % (birthday, birthmonth, birthyear)

    def save_csv(self, n, output_filename):
        """compile a list of people saved in CSV matching original address book format"""
        if n <= 0:
            raise self.NegSampleSizeException(\
                "Can't generate zero or negative sample sizes! (n = %d)" % (n))
        outputfile = file(output_filename, "wb")
        np = self.person()
        # swallow empty first instance
        abc = list(np.next().keys())
        wtr = csv.DictWriter(outputfile, self.fieldorder, extrasaction='ignore')
        # Write heading row in order of original contacts table
        # NB: leaves out some of the data generated
        wtr.writerow(dict(zip(self.fieldorder, self.fieldorder)))
        # Write people data
        for i in range(n):
            wtr.writerow(np.next())
        outputfile.close()
                           
if __name__ == "__main__":
    """
    generate a file, size no_of_people, list some names or dump all generated data to console
    """
    generate_file = False
    # save a file of random people
    if generate_file:
        no_of_people = 200
        RandomPerson().save_csv(n=no_of_people, output_filename = output_file("testing.csv"))
    else:
        # demonstrate producing a stream of people of any length
        new_contact = RandomPerson().person()
        justnames = True
        if justnames:
            for i in range(10):
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