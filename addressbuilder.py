import csv
import re
import random

from fieldmap import translateIn
from filelinks import lookup_file


class AddressBuilder:

    def __init__(self, filename=lookup_file("Addresses.csv")):
        self.address_generator = self._address()
        self.firstlineaddress_fld = "street"
        # load in all addresses for random-access
        addresses = tuple(csv.DictReader(open(filename)))
        self.addresses = tuple(translateIn(address) for address in addresses)

    def _address(self):
        """generator returning a random address"""
        while True:
            yield random.choice(self.addresses)

    def obfuscate_address(self):
        address = next(self._address())
        firstline = self.rewrite_address_numbers(address)
        address[self.firstlineaddress_fld] = "".join(firstline)
        return address

    def rewrite_address_numbers(self, person):
        firstline = re.split('(^[0-9]+)', person[self.firstlineaddress_fld])
        if len(firstline) != 1:
            for el in firstline:
                # every number that isn't a house number (street no, Level, flat etc.) is
                # replaced by a small number
                if el.isdigit(): el = str(random.randint(1, 5))
            if firstline[0] == '':
                # Initial number: choose from larger range for house numbers, including odd and even
                # TODO: normal distribution?
                firstline[1] = str(random.randint(0, 75) * 3 + 1)
        return firstline


if __name__ == '__main__':
    n = AddressBuilder()
    for i in range(5):
        print(n.obfuscate_address())



