__author__ = 'nick'

"""
Filelinks.py
Set of functions allowing code and data to find each other locally
Allows code to run from a memory key, network or local hard disc without
hard-coding file paths
"""

import os

def base_dir():
    """
    directory in which this module sits
    At present (Nov 2012) the module expects to find lookup tables and
    save datafiles to this same directory
    """
    return os.path.dirname(__file__)

def output_file(filename):
    """full path of file in same dir as this module"""
    return os.path.join(base_dir(), "output", filename)

def lookup_root():
    return os.path.join(base_dir(), "lookups")

def lookup_file(filename):
    """full path of file in same dir as this module"""
    return os.path.join(lookup_root(), filename)

def test_data_root():
    return os.path.join(base_dir(), "test data")


def test_data_output_file(filename):
    """where to put test data output file"""
    return os.path.join(test_data_root(), "output", filename)

def test_data_input_file(filename):
    """where to find test data filename"""
    return os.path.join(test_data_root(), "input", filename)
