
class LifterException(Exception):
    pass


class DoesNotExist(LifterException, ValueError):
    pass


class MultipleObjectsReturned(LifterException, ValueError):
    pass


class MissingAttribute(LifterException, ValueError):
    pass
