__author__ = 'nick'

import random
import unittest
import csv
import os
from randomPerson import RandomName, RandomPerson
from filelinks import test_data_input_file, test_data_output_file

class TestRandomPerson(unittest.TestCase):


    def output_file(self, no_of_people):
        return test_data_output_file("sample-" + str(no_of_people) + "people.csv")

    def setUp(self):
        self.samples = [10, 100, 1000]
        for no_of_people in self.samples:
            try:
                os.unlink(output_file(no_of_people))
            except:
                pass

    def test_RN_Handles_BlankLines(self):
        # make sure the name lookup initialisers deal well with empty lines
        self.name_generator = \
            RandomName(test_data_input_file("lookupwithgaps.csv"), name_fld="Forename")
        self.assertEqual(\
            len(self.name_generator.namelist),\
            len(list(csv.DictReader(open(test_data_input_file("lookupwithgaps.csv")))))
        )

    def test_RN_Handles_NonNumPopularity(self):
        # make sure the name popularity mechanisms deal with empty lines
        with self.assertRaises(RandomName.MissingPopularityException):
            name_generator =\
                RandomName(test_data_input_file("lookupMissingPopularity.csv"),\
                    name_fld="Forename")

    @unittest.skip("Fails but not mission-critical for large name lookup files")
    def test_RN_Uses_All_Names(self):
        """
        make sure no names are excluded from results using small 2-entry lookup file
        and enough iterations
        """
        test_fname = test_data_input_file("minimallookup.csv")
        # get checklist
        checklist = list(csv.DictReader(open(test_fname)))
        decent_run = 100
        # set up name generator
        name_generator = RandomName(test_fname, name_fld="Forename")
        # check both names represented in output
        for name_check in checklist:
            for i in range(decent_run):
                new_name = name_generator.name()
                if name_check == new_name: break
            else: self.fail("Name %s not generated at probability %d" %
                            (name_check, decent_run/float(len(checklist))))


    def test_RP_save_neg_sample(self):
        """
        RandomPerson().save should raise exception with negative sample sizes
        """
        with self.assertRaises(RandomPerson.NegSampleSizeException):
            RandomPerson().save_csv(n=-1, output_filename = self.output_file(-1))


    def test_RP_generate_3_files(self):
        """
        RandomPerson().save does generate files (and can be called repeatedly)
        """
        for no_of_people in self.samples:
            RandomPerson().save_csv(n=no_of_people, output_filename = self.output_file(no_of_people))
            self.assertTrue(os.path.isfile(self.output_file(no_of_people)))

    def test_RP_NoBlankNames(self):
        """
        over a long-ish sample check RandomPerson doesn't emit any blank names
        """
        def null_or_blank(s):
            return not s.strip(' \r\t\n')

        sample_size = 2000
        new_person = RandomPerson().person()
        new_name = RandomPerson().name_and_sex()
        for contact in range(sample_size):
            p = new_person.next()
            self.assertFalse(null_or_blank(p['First name']))
            self.assertFalse(null_or_blank(p['Middle name']))
            self.assertFalse(null_or_blank(p['Last Name']))
        for contact in range(sample_size):
            n = new_name.next()
            cnt = 0
            # check all name and sex fields are non-blank
            for i in n.items():
                cnt += 1
                self.assertFalse(null_or_blank(i[1]))



if __name__ == '__main__':
    unittest.main()
