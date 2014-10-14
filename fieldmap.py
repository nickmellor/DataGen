__author__ = 'nick'
"""
*********************** ETL Data Translation Engine *********************************
Transforms an input database into NameGen's internal format, where it can be
transformed, then translates field names into a format to suit the output database

*************************************************************************************

"""

import yaml
import filelinks
import os

class FilterDefaultException(Exception):
    pass

# master list of field names used internally
cfgpath = os.path.join(filelinks.base_dir(), "translations.yaml")
cfg = yaml.load(open(cfgpath, 'r').read())
INTERNAL_NAMES = cfg['Internal_fields']
INCOMING_FILTERS = cfg['Incoming']
#print "Incoming Filters:\n{}".format(INCOMING_FILTERS)
OUTGOING_FILTERS = cfg['Outgoing']
# If no outgoing filter exists for a corresponding incoming filter
# auto-generate one by reversing field mappings
autofilters = {fm: {v: k for k, v in INCOMING_FILTERS[fm].items() if v}
               for fm in INCOMING_FILTERS
               if fm not in OUTGOING_FILTERS}
autofilters = {k: v for k, v in autofilters.items() if v}
OUTGOING_FILTERS.update(autofilters)
# for filt in autofilters_for:
#     print 'filt: ', filt
#
#
#     for k, v in filt.items():
#         print 'v: ', v
#         if v:
#             OUTGOING_FILTERS.update(autofilters_for[filt])
#print 'Outgoing filters:\n', OUTGOING_FILTERS
DEFAULT_FILTER = cfg['Default_filter']
if DEFAULT_FILTER not in INCOMING_FILTERS:
    raise FilterDefaultException("Default filter '{}' could not be found".format(DEFAULT_FILTER))



# TODO-- optional data
#   -- File As
#   -- full name in one field
#   -- full name as "surname, forenames"
#   -- birthday without year

class BadTranslationTable(Exception):
    pass

# # check that internal names match incoming translations
#
for filt in INCOMING_FILTERS:
    # print filt, ":"
    # print INCOMING_FILTERS[filt]
    fieldcheck = [(filt, k, v, v in INTERNAL_NAMES)
                  for k, v in INCOMING_FILTERS[filt].items() if v]
    # print "Check {0}---\n {1}".format(filt, fieldcheck)
    errors = [f for f in fieldcheck if not f[3]]
    if errors:
        print("\n".join([
                "'{0}' is not an internal field ('from' field in incoming filter {1} is '{2}')".format(
                    f[2], f[0], f[1])
                for f
                in errors]))
        raise BadTranslationTable('Fault in Incoming Translation Table')

for filt in OUTGOING_FILTERS:
    fieldcheck = [(filt, k, v, k in INTERNAL_NAMES)
                  for k, v
                  in OUTGOING_FILTERS[filt].items() if v is not None]
    errors = [f for f in fieldcheck if not f[3]]
    if errors:
        print("\n".join(["'{0}' is not an internal field ('from' field in outgoing filter '{1}' is '{2}')".format(
         f[2], f[0], f[1])
           for f
           in errors]))
        raise BadTranslationTable('Fault in Outgoing Translation Table')

# TODO-- output field order at least for csv
# TODO-- convert translation mechanisms into a class

# def transform(p, fieldmapping, passthru=False):
#     """
#     convert fieldnames between internal and external formats
#     Translations that would produce a blank or None fieldname are dropped
#
#     passthru (True/False)
#     passthru==True: Any fields without fieldmapping will pass through unaltered
#     passthru==False: if field is not in fieldmap, field will be dropped
#     """
#
#     trans = {}
#     if passthru:
#         # 'pass-thru' any unmapped fields unchanged
#         trans = {k: v for k, v in p.items()
#                  if k not in fieldmapping}
#     # add the rest, dropping fields mapped to None
#     trans.update({v: p[k] for k, v
#                   in fieldmapping.items() if k in p.keys() and v})
#     return trans
#
# def translateIn(p, passthru=False):
#     return transform(p, fieldmapping=INCOMING_TRANSLATION, passthru=passthru)
#
# def translateOut(p, passthru=False):
#     return transform(p, fieldmapping=OUTGOING_TRANSLATION, passthru=passthru)