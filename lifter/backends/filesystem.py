from .python import AbstractPythonManager



class FileManager(AbstractPythonManager):
    def __init__(self, *args, **kwargs):
        self.path = kwargs.pop('path')
        super(FileManager, self).__init__(*args, **kwargs)

    def get_values(self):
        with open(self.path) as f:
            return [self.model(**self.parser.parse(line)) for line in f]
