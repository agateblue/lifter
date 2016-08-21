from .python import DummyStore


class FileStore(DummyStore):

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(FileStore, self).__init__(*args, **kwargs)

    def load(self, model, adapter):
        with open(self.path) as f:
            return [adapter.parse(line, model) for line in f]
