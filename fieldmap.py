__author__ = 'nick'
"""
*********************** ETL Data Translation Engine *********************************
Transforms an input database into its internal format, where it can be transformed,
then translates field names into a format to suit the output database

*************************************************************************************

"""

# master list of field names used internally
INTERNAL_NAMES = ('birthday', 'salutation', 'first_name', 'middle_name', 'last_name',
                  'mob', 'phone', 'email',
                  'street', 'state', 'suburb_town', 'postal_code',
                  'sex', 'title', 'website', 'password', 'position', 'company')

# TODO-- optional data
#   -- File As
#   -- full name in one field
#   -- full name as "surname, forenames"
#   -- birthday without year

class BadTranslationTable(Exception):
    pass

# Translation for Outlook CSV incoming
# The incoming translation will be the addresses to obfuscate
OUTLOOK_MAP_INCOMING = {
    'Birthday'    : None,
    'Company'     : None,
    'Title'       : 'position',
    'First name'  : 'first_name',
    'Middle name' : None,
    'Last Name'   : 'last_name',
    'Mobile'      : 'mob',
    'Phone'       : 'phone',
    'Email'       : 'email',
    'Fax'         : None,
    'Street'      : "street",
    'State'       : 'state',
    'Suburb'      : 'suburb_town',
    'Postcode'    : 'postal_code',
    'Sex'         : None,
    'Title'       : None,
    'Website'     : 'website',
    'password'    : 'password'}

OUTLOOK_MAP_OUTGOING = {v:k for k,v in OUTLOOK_MAP_INCOMING.items() if v}

# check that internal names match incoming translations

print ('Testing Incoming Translations...')
incoming_maps = (OUTLOOK_MAP_INCOMING,)
for inc in incoming_maps:
    fieldcheck = [(k, v, v in INTERNAL_NAMES)
                  for k, v in inc.items() if v is not None]
    errors = [f for f in fieldcheck if not f[2]]
    if errors:
        print("\n".join([
                "'{0}' is not an internal field (original is '{1}').".format(f[1], f[0])
                for f
                in errors]))
        raise BadTranslationTable('Fault in Incoming Translation Table')

# which incoming translation to use by default
INCOMING_TRANSLATION = OUTLOOK_MAP_INCOMING

# key is internal name, value is output fieldname
SOME_OUTPUT_FORMAT = {
    'website'     : 'website',
    'first_name'  : 'first_name',
    'last_name'   : 'last_name',
    'street'      : 'street',
    'title'       : 'title',
    'sex'         : 'gender',
    'position'    : None,
    'phone'       : 'telephone',
    'state'       : 'state',
    'birthday'    : 'birthday',
    'postal_code' : 'zip',
    'suburb_town' : 'city',
    'salutation'  : 'dear',
    'mob'         : 'mob',
    'password'    : 'passwd',
    'email'       : 'email'}

print ('Testing Outgoing Translations...')
outgoings = (SOME_OUTPUT_FORMAT, OUTLOOK_MAP_OUTGOING)
for outgoing_translation in outgoings:
    fieldcheck = [(k, v, k in INTERNAL_NAMES)
                    for k, v
                    in outgoing_translation.items() if v is not None]
    errors = [f for f in fieldcheck if not f[2]]
    if errors:
        print("\n".join([
        "'{0}' is not an internal field (output field is '{1}').".format(f[0], f[1])
        for f
        in errors]))
        raise BadTranslationTable('Fault in Outgoing Translation Table')

# which output translation to use by default
OUTGOING_TRANSLATION = SOME_OUTPUT_FORMAT

# TODO-- output field order at least for csv
# TODO-- convert translation mechanisms into a class

def transform(p, fieldmapping, passthru=False):
    """
    convert fieldnames between internal and external formats
    Translations that would produce a blank or None fieldname are dropped

    passthru (True/False)
    If True, the translator is a "pass-thru" translator. Any fields it doesn't know
    what to do with it passes through unaltered.

    A None or blank Value in a fieldmapping (dict) member
    will cause that field to be dropped

    """
    if passthru:
        # 'pass-thru' any unmapped fields unchanged
        trans = {k:v for k, v in p.items()
                 if k not in fieldmapping}
    else:
        # only fields with a fieldmapping are output
        trans = {}
    # add the rest, dropping fields mapped to None
    trans.update({v:p[k] for k, v
                  in fieldmapping.items() if k in p.keys() and v})
    return trans

def translateIn(p, passthru=False):
    return transform(p, fieldmapping=INCOMING_TRANSLATION, passthru=passthru)

def translateOut(p, passthru=False):
    return transform(p, fieldmapping=OUTGOING_TRANSLATION, passthru=passthru)