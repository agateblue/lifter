from .python import IterableStore, RefinedIterableStore, PythonManager


class RefinedFileStore(RefinedIterableStore):

    manager_class = PythonManager

    def get_all_values(self, query):
        with open(self.parent.path) as f:
            return [self.model(**self.adapter.parse(line)) for line in f]

class FileStore(IterableStore):
    refined_class = RefinedFileStore

    def __init__(self, path):
        self.path = path
