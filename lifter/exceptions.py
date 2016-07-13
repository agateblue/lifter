
class LifterException(Exception):
    pass


class DoesNotExist(LifterException, ValueError):
    pass


class MultipleObjectsReturned(LifterException, ValueError):
    pass


class MissingAttribute(LifterException, ValueError):
    pass


class UnsupportedQuery(LifterException, ValueError):
    def __init__(self, message, query):
        super(UnsupportedQuery, self).__init__(message)
        self.query = query
