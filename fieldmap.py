__author__ = 'nick'

# NB null entries are not imported

# field names used internally
INTERNAL_NAMES = ('birthday', 'salutation', 'first_name', 'last_name', 'mob', 'phone',
                  'email', 'street', 'state', 'suburb_town', 'postal_code',
                  'sex', 'title', 'website', 'password', 'position')

Company,First name,Last Name,\
Title,Street,Suburb,State,Postcode,\
Phone,Fax,Mobile,Email,Website

# Translation for Outlook CSV incoming
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
incomings = (OUTLOOK_MAP_INCOMING,)
for inc in incomings:
    result = all([field in INTERNAL_NAMES
                        for field
                        in inc.values()
                        if field])
    print(result)