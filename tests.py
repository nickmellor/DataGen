__author__ = 'nick'

import unittest
import csv
import os
from randomPerson import WeightedChoice, RandomContact
from filelinks import test_data_input_file, test_data_output_file
from collections import Counter

def numbered_sample_output_file(no):
    return test_data_output_file('sample-' + str(no) + '.csv')

class TestRandomPerson(unittest.TestCase):


    def setUp(self):
        # iterations to ensure secure testing of binary values (e.g. sex)
        self.binary_check_sample_size = 2000
        # a sample with a bit of length to test trends
        self.medium_sample_size = 2000
        # range of small sample sizes
        self.no_of_small_samples = 50
        # number of small samples: (0 should fail, 1 is an important test case)
        self.small_sample_sizes = range(1,self.no_of_small_samples + 1)
        # delete test output files
        for no_of_people in self.small_sample_sizes:
            try:
                os.unlink(numbered_sample_output_file(no_of_people))
            except OSError:
                pass

    def tearDown(self):
        pass

    def test_RN_Handles_BlankLines(self):
        # make sure the name lookup initialisers deal well with empty lines
        self.name_generator = \
            WeightedChoice(test_data_input_file("lookupwithgaps.csv"), name_fld="Forename")
        self.assertEqual(
            len(self.name_generator.items),
            len(list(csv.DictReader(open(test_data_input_file("lookupwithgaps.csv")))))
        )

    def test_RN_Handles_NonNumPopularity(self):
        # make sure the name popularity mechanisms deal with empty lines
        with self.assertRaises(WeightedChoice.MissingPopularityException):
            name_generator = WeightedChoice(
                                test_data_input_file("lookupMissingPopularity.csv"),
                                                        name_fld="Forename")

    def test_RN_Uses_All_Names(self):
        """
        test that RandomNames uses all available options.
        Method: probabilistic test to make sure no names are excluded from results using
        small lookup file with just a few items and enough iterations to make all items
        extremely likely to be chosen at least once
        """
        test_fname = test_data_input_file("minimallookup.csv")
        # get checklist
        checklist = list(csv.DictReader(open(test_fname)))
        # how many samples make it *extremely* unlikely that any item was not selected
        # at least once?
        # set up name generator
        name_generator = WeightedChoice(test_fname, name_fld="Forename")
        # check all names are represented in output
        for name_check in checklist:
            for i in range(self.binary_check_sample_size):
                new_name = name_generator.name()
                if name_check["Forename"] == new_name: break
            else:
                self.fail("Name %s (1 of %d) was not generated even after %d iterations"\
                          % (name_check["Forename"],
                             len(name_generator.items),
                             self.binary_check_sample_size))


    def test_RP_save_zero_or_neg_sample(self):
        """
        RandomPerson().save should raise exception with negative sample sizes
        """
        with self.assertRaises(RandomContact.NegSampleSizeException):
            RandomContact().save(
                no_of_people=-1,
                output_filename = test_data_output_file("sample-minus1-items"))
        with self.assertRaises(RandomContact.NegSampleSizeException):
            RandomContact().save(
                no_of_people=-1,
                output_filename = test_data_output_file("sample-zero-items"))


    def test_RP_generate_many_files(self):
        """
        RandomPerson().save does generate files (and can be called repeatedly)
        """

        for no_of_people in self.small_sample_sizes:
            output_filename = numbered_sample_output_file(no_of_people)
            RandomContact().save(
                no_of_people,
                output_filename=output_filename,
                output_filetype='csv')
            self.assertTrue(os.path.isfile(output_filename),
                msg='Sample %s not created' % os.path.isfile(output_filename))
            self.assertEqual(
                len(list(csv.DictReader(open(output_filename)))),
                no_of_people,
                msg="Sample %d should contain %d elements. Contains %d (%s)" %\
                    (no_of_people,
                     no_of_people,
                     len(list(csv.DictReader(output_filename))),
                     output_filename)
            )

    def test_RP_NoBlankNames(self):
        """
        over a good-sized sample check RandomPerson doesn't emit any blank names
        """
        def null_or_blank(s):
            return not s.strip(' \r\t\n')

        name = RandomContact().gendered_name()
        for contact in range(self.medium_sample_size):
            n = name.next()
            cnt = 0
            # check all name and sex fields are non-blank
            for i in n.items():
                cnt += 1
                self.assertFalse(null_or_blank(i[1]))

    def test_RP_sexes_roughly_even(self):
        sexes_variation_percent = 15.0
        name = RandomContact().gendered_name()
        sex_count = Counter()
        for contact in range(self.binary_check_sample_size):
            p = name.next()
            sex_count[p['sex']] += 1
        print sex_count.items()
        # check sexes are equally numbered to within a reasonable tolerance (e.g. 10%)
        # Males outnumber females by a percentage point or two
        self.assertAlmostEqual(
            sex_count['male'] + 2.0/100.0 * self.binary_check_sample_size,
            sex_count['female'],
            delta=self.binary_check_sample_size * sexes_variation_percent / 100.0 + 1.0)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRandomPerson)
    unittest.TextTestRunner(verbosity=2).run(suite)
