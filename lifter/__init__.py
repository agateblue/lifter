# -*- coding: utf-8 -*-

__author__ = 'Eliot Berriot'
__email__ = 'contact@eliotberriot.com'
__version__ = '0.1.0'

from .lifter import Manager, DoesNotExist, MultipleObjectsReturned

def load(values):
    return Manager(values)
