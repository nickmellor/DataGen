Random Personal Data Generator
==============================

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

