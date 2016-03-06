
from . import base
from .. import query


class PythonModel(base.BaseModel):
    __metaclass__ = base.BaseModelMeta
    path_class = query.Path
    
    @classmethod
    def load(cls, values):
        return query.QuerySet(values)
