import os
import hashlib
from dates import birthday
from filelinks import base_dir
from namebuilder import NameBuilder
from addressbuilder import AddressBuilder


class RandomContact:
    """
    generate a contact record with random but believable personal data
    """

    def __init__(self, lookup_root=os.path.normpath(os.path.join(base_dir(), "lookups")),
                 email_prefix='rp_', email_domain='@gmail.com', password='test123'):
        """
        lookup_root specifies where to find lookup tables
        """
        self.lookup_root = lookup_root
        self.website_fld = "website"
        self.fieldorder = []
        self.name_builder = NameBuilder()
        self.address_builder = AddressBuilder()
        self.email_prefix = email_prefix
        self.email_domain = email_domain
        self.password = password

    def contact(self):
        """
        generator returning random but fairly realistic personal contact details
        Data is modelled on an existing
        address list and name frequency tables, with various fields
        obfuscated for privacy."""
        id = 1
        while True:
            person = next(self.address_builder.obfuscated_address())
            person.update(birthday())
            # Override or insert surname and forename info
            person.update(next(self.name_builder.gendered_name()))
            username = self.email_address(person)
            # Use username for email as well
            # Email domain name could be more sophisticated...
            person.update({"email": self.email_address(person),
                           "username": username,
                           "password": "test123"})
            yield person
            id += 1

    def email_address(self, person):
        return "{base}+{prefix}{username}@{domain}".format(prefix=self.email_prefix,
                    base='thebalancepro', username=self.username(person),
                    domain=self.email_domain)

    @staticmethod
    def username(person):
        return "{name}-{hash}".format(name=person["first_name"],
            hash=hashlib.md5(repr(person).encode()).hexdigest()[:5])


if __name__ == "__main__":
    # demonstrate producing a stream of people of any length
    contact = RandomContact().contact()
    justnames = False
    if justnames:
        for i in range(50):
            p = next(contact)
            print("Here's one...")
            print("%s, %s %s" % (p["Last Name"].upper(), p["First name"], p["Middle name"]))
    else:
        for i in range(10):
            p = next(contact)
            print()
            print("==================================")
            print()
            for j in p.items():
                print("%s: %s" % (j[0], j[1]))
            print()
