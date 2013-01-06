__author__ = 'nick'
######################### Random Person Generator ###################################
#########################    by Nick Mellor       ###################################
#########################     Version 1.0         ###################################
#########################      Nov 2012           ###################################
"""Random Personal Data Generator
Generates random details of fictitious people (for testing purposes?)

Includes:
full name, sex, birthdate, address, web address,
email address etc. based on an existing contact list, name popularity data and
basic demographics

Generates CSV file, YAML file (Django fixture) or a continuous stream of realistic
but random personal data in Python dictionary format

Random data is based on obfuscated real-world addresses

An ordinary contact list can be dropped into the generator unchanged
to act as model data-- you can use your own address book to generate realistic
contact details. The initial file format is Outlook export CSV but can easily be
modified for other sources

Transformations:

Typically

Obfuscations include:
  - all numbers in first line of address are changed
  - names are randomised (popularity-adjusted)
  - web addresses are decoupled from postal addresses
  - usernames and emails are regenerated
  - birthdays are randomised (realistically)

Performance:
1000+ people per second (2GHz laptop, 200 entries in address file)

Use:
See examples at end of module

Future (Nov 2012):
- With the right datafiles, could mix names from different nationalities or demographics
  (e.g. software developers, middle managers, single parents) and/or generate data for other
  purposes such as organisation names, job titles, fruit and vegetable orders etc.
- remove string literals from code (e.g. "First name")
- Better unit testing

Updates:
Nov 2012-- unit tests, minor refactorings and code commenting
"""

import yaml
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
    class MissingPopularityException(RandomNameException):
        """
        missing or malformed popularity field contents
        """
        pass

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
            name_candidate[self.running_total_fld] = running_total
            # Exponentiate 0-5 score for popularity
            try:
                popularity = math.exp(float(name_candidate[self.popularity_fld]))
            except:
                raise self.MissingPopularityException(\
                    "Popularity should be 0..5 on name %s in file %s" % \
                    (name_candidate[self.name_fld], self.filename))
            # a name with index n is matched if
            # running_total(n) <= pindrop < running_total(n+1)
            # in the sorted list
            running_total += popularity
        # total_popularity used later to define range over which to choose a name
        self.total_popularity = running_total


    def name(self):
        """
        returns a random name with frequency based on a subjective
        popularity rating e.g. for male forenames, "John" will be emitted often,
        "Bartholomew" rarely
        """
        return self.all()[self.name_fld]

    def all(self):
        """return name and pass through other information in lookup table"""
        # pick a random spot in the popularity interval over all words
        ## Next line: stick an oar in to verify unit test test_RN_Uses_All_Names
        ##self.total_popularity = self.namelist[-1][self.running_total_fld]
        pindrop = random.uniform(0.0, self.total_popularity)
        # which word did that spot fall on? (Linear search)
        i = 0
        end_of_list = len(self.namelist) - 1
        item, next_item = self.namelist[0], self.namelist[1]
        while i < end_of_list:
            if item[self.running_total_fld] <= pindrop < next_item[self.running_total_fld]:
                return item
            i += 1
            item, next_item = next_item, self.namelist[i]
        # edge case: pindrop > last word running total: means last word should be chosen
        return item


import fieldmap
class RandomPerson:
    """
    generate a "person" record with random but believable personal data
    """
    class NegSampleSizeException(RandomPersonException):
        """
        Negative or zero sample size passed to .save_csv
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


    def _map_fields(self, p, fieldmap_override=None):
        """
        select out and rename the fields as appropriate for the client
        application
        """
        if fieldmap_override is None:
            fieldmap_override = fieldmap.FIELDMAP
        return {v:p[k] for k,v in fieldmap_override.items() if v}

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

    def gendered_name(self):
        """
        generate forenames, surname and sex
        Forenames must match in gender
        e.g. "Sarah Jane" and "Robert James" are okay
        but not "Alice Brett" or "Rose Frank"
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
            person["Birthday"] = self.birthday()
            # Override or insert surname and forename info
            person.update(self.gendered_name().next())
            # Generate fake email addresses, usernames and ids

            # OPTIONS:
            #   - Simple username: unique per run
            #username = "test" + str(id)

            #   - More sophisticated: good uniqueness but still contains first name
            # Removing [:5] or increasing 5 to n
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
         and birthyear % 4 == 0
         and (birthyear % 100 != 0 or birthyear % 400 == 0)):
            lastdayofmonth = 29
        # choose day of month
        birthday = int(random.uniform(1.0, 31.0) * (float(lastdayofmonth) / 31) + 1.0)
        return "%d/%d/%d" % (birthday, birthmonth, birthyear)

    def save(self,
             no_of_people,
             output_filename,
             output_filetype='django_yaml_fixture',
             yaml_entity='Customer'):
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
                field_header = [fieldmap.FIELDMAP[r]
                                for r
                                in self.fieldorder
                                if fieldmap.FIELDMAP[r]]
                wtr = csv.DictWriter(outputfile, field_header, extrasaction='ignore')
                wtr.writeheader()
            for i in range(no_of_people):
                if output_filetype == 'csv':
                    wtr.writerow(self._map_fields(np.next()))
                elif output_filetype == 'django_yaml_fixture':
                    outputfile.write(yaml.dump({'model': yaml_entity,
                                                'fields': self._map_fields(np.next())}))



if __name__ == "__main__":
    """
    generate a file, size no_of_people, list some names or dump all generated data to console
    """
    generate_file = True
    # save a file of random people
    if generate_file:
        no_of_people = 10
        RandomPerson().save(no_of_people,
                            output_filename=output_file("testing.csv"),
                            output_filetype='csv')
        RandomPerson().save(no_of_people,
                            output_filename=output_file("testing.yaml"),
                            output_filetype='django_yaml_fixture',
                            yaml_entity='groceries.Customer')
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