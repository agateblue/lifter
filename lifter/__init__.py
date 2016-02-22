# -*- coding: utf-8 -*-

__author__ = 'Eliot Berriot'
__email__ = 'contact@eliotberriot.com'
__version__ = '0.1.1'

from .query import Manager, DoesNotExist, MultipleObjectsReturned, Q
from . import lookups
from .lookups import *
from .aggregates import *
from . import utils

def load(values, *args, **kwargs):
    return Manager(values, *args, **kwargs)
