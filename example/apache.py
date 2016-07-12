import datetime

from lifter import models
from lifter.adapters import RegexAdapter
from lifter.backends import filesystem


class LogEntry(models.Model):
    ip = models.CharField()
    date = models.DateTimeField()
    method = models.CharField()
    request_path = models.CharField()
    http_version = models.CharField()
    status_code = models.IntegerField()
    response_size = models.IntegerField()
    referrer = models.CharField()
    user_agent = models.CharField()


class LogEntryFileAdapter(RegexAdapter):

    regex = '(?P<ip>[(\d\.)]+) - - \[(?P<date>.*?) -(.*?)\] "(?P<method>\w+) (?P<request_path>.*?) HTTP/(?P<http_version>.*?)" (?P<status_code>\d+) (?P<response_size>\d+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'

    def clean_date(self, data, value, model, field):
        date_format = '%d/%b/%Y:%H:%M:%S'
        return field.to_python(self, value, date_format=date_format)


store = filesystem.FileStore(path='/tmp/apache.log')
manager = store.query(LogEntry, adapter=LogEntryFileAdapter())
