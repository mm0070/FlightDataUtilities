# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Utilities for looking up VMO/MMO for various aircraft.
'''

##############################################################################
# Imports


from flightdatautilities.aircrafttables.interfaces import MaximumSpeed_Fixed


##############################################################################
# Constants

# The format for the following mappings should match the following:
#
#   {
#       'name': (class, args),
#       ...
#   }
#
# Where the arguments should abide by the following:
#
#   - name:   model, series or family name of the aircraft. (string)
#   - class:  a class implementing MaximumSpeed.
#   - args:   arguments to be passed to the MaximumSpeed constructor (mixed)
#
# The format of args is (vmo, mmo) and the types depends on the class:
#
#   - MaximumSpeed_Fixed:  integer or float.
#   - MaximumSpeed_Range:  (low, high, value) where low to high is the altitude
#                          range and value is an integer or float.
# 
# Passing None instead will result in a masked zero array being returned.
#
# Passing an empty args tuple () is equivalent to (None, None).


MAX_SPEED_MODEL_MAP = {}


MAX_SPEED_SERIES_MAP = {}


MAX_SPEED_FAMILY_MAP = {
    'B737 Classic': (MaximumSpeed_Fixed, (340, 0.82)),
}
