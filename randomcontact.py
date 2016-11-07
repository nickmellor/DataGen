import fieldmap
import os
import hashlib
import re
from fieldmap import translateIn, translateOut
from birthday import birthday
import yaml
from filelinks import base_dir
from namebuilder import NameBuilder


class RandomContact:
    """
    generate a contact record with random but believable personal data
    """

    def __init__(self, lookup_root=os.path.normpath(os.path.join(base_dir(), "lookups"))):
        """
        lookup_root specifies where to find lookup tables
        """
        self.lookup_root = lookup_root

        self.website_fld = "website"

        self.fieldorder = []
        self.name_builder = NameBuilder()

    def lookup_file(self, filename):
        """return full path of a filename by prepending root directory"""
        return os.path.join(self.lookup_root, filename)

    def person(self):
        """generator returning random but fairly realistic personal data:
        name, sex, address, username, password, birthday, email,
        website etc. Data is modelled on an existing
        address list and name frequency tables, with various fields
        obfuscated for privacy."""
        id = 1
        while True:
            person = self.obfuscate_address()
            person["birthday"] = birthday()
            # Override or insert surname and forename info
            person.update(next(self.name.gendered_name()))
            username = self.email_address(person)
            # Use username for email as well
            # Email domain name could be more sophisticated...
            person.update({"email": username + "@bendigotraders.org",
                           "username": username,
                           "password": "test"})
            yield person
            id += 1

    def email_address(self, person):
        return "{name}-{hash}".format(name=person["first_name"],
            hash=hashlib.md5(repr(person).encode()).hexdigest()[:5])

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
                wtr = self.setup_csv(outputfile)
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

    def setup_csv(self, outputfile):
        # Write heading row in order of original contacts table
        # todo-nm outgoing translations passim
        # print("fieldorder", self.fieldorder)
        field_header = [fieldmap.OUTGOING_TRANSLATION[r]
                        for r
                        in self.fieldorder
                        if fieldmap.OUTGOING_TRANSLATION[r]]
        wtr = csv.DictWriter(outputfile, field_header, extrasaction='ignore')
        wtr.writeheader()
        return wtr


# todo optional primary key, currently only implemented for YAML fixture

if __name__ == "__main__":
    """
    generate a file, size no_of_people, list some names or dump all generated data to console
    """
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
                    print()
                    for j in p.items():
                        print("%s: %s" % (j[0], j[1]))
                    print()
