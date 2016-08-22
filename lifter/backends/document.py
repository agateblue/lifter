import contextlib

from .python import DummyStore
from six.moves.urllib.request import urlopen

class DocumentStore(DummyStore):
    """
    Return results from arbitrary static
    sources (HTTP, local file system, etc.)
    """
    def __init__(self, url, *args, **kwargs):
        self.url = url
        self.parser = kwargs.pop('parser', None)
        super(DocumentStore, self).__init__(*args, **kwargs)

    def get_document(self):
        return urlopen(self.url)

    def parse_document(self, document, model, adapter):
        if not self.parser:
            return self.from_lines(document, model, adapter)
        else:
            return self.from_parser(document, model, adapter)

    def from_parser(self, document, model, adapter):
        parsed = self.parser.parse(document.read())
        return [adapter.parse(result, model, store=self) for result in parsed]

    def from_lines(self, document, model, adapter):
        return [adapter.parse(line, model, store=self) for line in document]

    def load(self, model, adapter):
        with contextlib.closing(self.get_document()) as document:
            return self.parse_document(document, model, adapter)
