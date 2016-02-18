# -*- coding: utf-8 -*-

__author__ = 'Eliot Berriot'
__email__ = 'contact@eliotberriot.com'
__version__ = '0.1.0'

from .query import Manager, DoesNotExist, MultipleObjectsReturned, Q
from . import lookups
from .lookups import *
from .aggregates import *

def load(values):
    return Manager(values)
