Random "contact details" generator
Written by Nick Mellor
June 2009: version 1.0

Program: randomperson.py
Needs datafiles: Addresses.csv, forenames.csv

Generates unlimited random people with name, birthday, sex, user id, password, email
Written for testing web/database apps under realistic data situations

Features:
- Obfuscates real mail addresses to get realistic random addresses. you can use your own address book
- chooses surnames and forenames based on popularity score
- optionally chooses middle names
- md5 hash-based email addresses and passwords