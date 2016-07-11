from .python import IterableStore


class FileStore(IterableStore):
    def __init__(self, path):
        self.path = path

    def get_all_values(self, query):
        with open(self.path) as f:
            return [query.hints['model'](**query.hints['parser'].parse(line)) for line in f]
