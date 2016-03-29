
from . import query
from .backends.base import BaseModelMeta, BaseModel
from .fields import *

def Model(name):
    from .backends import python
    return BaseModelMeta(name, (python.PythonModel,), {})
