import json



class Parser(object):
    def parse(self, content):
        raise NotImplementedError()


class JSONParser(Parser):
    def parse(self, content):
        return json.loads(content)
