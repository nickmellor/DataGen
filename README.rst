DataGen

"Out of the Box" generator of pseudo-random personal data. Data is
"realistic". Names sound like real names and occur with real-world frequency,
gender, birthdays etc.

Useful for code testing and load-modelling

Output
======

- via a Python generator (potentially unlimited names)

- as a YAML file

- as a CSV file


Use Out of the Box
==================

This application should download and run as is on a hard disk or memory key in any OS
so long as Python is installed. Examples of use are given in the ``RandomPerson.py`` module:

>>> python RandomPerson.py


Configurable
=================

Example popularity tables are included for a selection of English-language surnames
and forenames. The present files mark rare names with a rating of zero,
very common names with a rating of 5.


Future Facilities
=================

- SQL output

- data modelling for non-personal data

- obfuscating a production database for use by analysts without security clearance

Author
======

`Nick Mellor <http://www.back-pain-self-help.com>`_, an Alexander Technique teacher
and Python/Django developer in Newstead, Central Victoria, Australia