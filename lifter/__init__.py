# -*- coding: utf-8 -*-

__author__ = 'Eliot Berriot'
__email__ = 'contact@eliotberriot.com'
__version__ = '0.2.1'

from . import managers
Manager = managers.Manager

from .exceptions import *
from . import exceptions

from .query import Path, Query, QuerySet

from . import lookups
from .lookups import *
from .aggregates import *

from . import models

def load(values, *args, **kwargs):
    return Manager(values, *args, **kwargs)
