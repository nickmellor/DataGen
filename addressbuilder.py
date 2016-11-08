import csv
import re
import random

from fieldmap import translateIn, translateOut
from filelinks import lookup_file


class AddressBuilder:

    def __init__(self, filename=lookup_file("Addresses.csv")):
        self.address_generator = self._address()
        self.firstline_field = "street"
        # load in all addresses for random-access
        addresses = tuple(csv.DictReader(open(filename)))
        self.addresses = tuple(translateIn(address) for address in addresses)

    def _address(self):
        """generator returning a random address"""
        while True:
            yield random.choice(self.addresses)

    def obfuscate_address(self):
        while 1:
            address = next(self._address())
            if address[self.firstline_field]:
                break
        address[self.firstline_field] = self.obfuscated_firstline(address)
        return address
        # return address

    def obfuscated_firstline(self, person):
        # TODO: deal with '12-15 Collins Street' where numbers should be similar in size
        # (not translated into 5-143 Collins Street)
        firstline = re.split('(^[0-9]+)', person[self.firstline_field])
        if len(firstline) != 1:
            for el in firstline:
                # every number that isn't a house number (street no, Level, flat etc.) is
                # replaced by a small number
                if el.isdigit(): el = str(random.randint(1, 5))
            if firstline[0] == '':
                # Initial number: choose from larger range for house numbers, including odd and even
                # TODO: normal distribution?
                firstline[1] = str(random.randint(0, 75) * 3 + 1)
        return "".join(firstline)


if __name__ == '__main__':
    n = AddressBuilder()
    for i in range(5):
        print(n.obfuscate_address())



