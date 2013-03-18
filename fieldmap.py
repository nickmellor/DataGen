__author__ = 'nick'
"""
*********************** Translation Engine for NAMEGEN ******************************
NameGen translates an address database into its internal format, shuffles it up
then translates it into a final output format to suit the database, application or
other fixed format on the receiving end of NameGen's random contact data.

This file contains the code and data for translating between input, internal
 and output formats
*************************************************************************************

"""

# master list of field names used internally
INTERNAL_NAMES = ('birthday', 'salutation', 'first_name', 'last_name', 'mob', 'phone',
                  'email', 'street', 'state', 'suburb_town', 'postal_code',
                  'sex', 'title', 'website', 'password', 'position', 'company')

# TODO-- optional data
#   -- File As
#   -- full name in one field
#   -- full name as "surname, forenames"
#   -- birthday without year

class BadTranslationTable(BaseException):
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


# check that internal names match incoming translations

print ('Testing Incoming Translations...')
incomings = (OUTLOOK_MAP_INCOMING,)
for inc in incomings:
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
outgoings = (SOME_OUTPUT_FORMAT,)
for outgoing_translation in outgoings:
    fieldcheck = [(k, v, k in INTERNAL_NAMES)
                  for k, v in outgoing_translation.items() if v is not None]
    errors = [f for f in fieldcheck if not f[2]]
    if errors:
        print("\n".join([
        "'{0}' is not an internal field (output field is '{1}').".format(f[0], f[1])
        for f
        in errors]))
        raise BadTranslationTable('Fault in Outgoing Translation Table')

# which output translation to use by default
OUTGOING_TRANSLATION = SOME_OUTPUT_FORMAT

# TODO-- output field order at least for csv)
# TODO-- convert translation mechanisms into a class

def translate(p, fieldmapping, passthru):
    """
    convert fieldnames between internal and external formats
    Translations that would produce a blank or None fieldname are dropped

    The translator is a "pass-thru" translator. If it has no instructions
    about a particular field, it lets the field through unaltered. Only a
    None or blank fieldname will cause that field to be dropped
    """
    if passthru:
        # 'pass-thru' fields: no translation
        trans = {k:v for k,v in p.items()
                 if k not in fieldmapping}
    else:
        trans = {}
    # add the rest, dropping fields mapped to None
    trans.update({v:p[k] for k,v
                  in fieldmapping.items() if ((k in p.keys()) and v)})
    return trans

def translateIn(p, passthru=True):
    return translate(p, fieldmapping=INCOMING_TRANSLATION, passthru=passthru)

def translateOut(p, passthru=True):
    return translate(p, fieldmapping=OUTGOING_TRANSLATION, passthru=passthru)