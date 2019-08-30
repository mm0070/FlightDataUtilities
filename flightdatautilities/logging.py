import datetime
import logging
import os
import queue
import socket
import sys
import threading

import elasticsearch
import elasticsearch.helpers


class Queue(queue.Queue):

    def drain(self):
        with self.mutex:
            try:
                return self.queue
            finally:
                self._init(self.maxsize)


class Serializer(elasticsearch.serializer.JSONSerializer):

    def default(self, data):
        try:
            return super().default(data)
        except TypeError:
            return str(data)


class ConsoleFormatter(logging.Formatter):
    _color_map = {
        logging.CRITICAL: '1;31',
        logging.ERROR: '31',
        logging.WARNING: '33',
        logging.INFO: '97',
        logging.DEBUG: '37',
    }
    _emoji_map = {
        logging.CRITICAL: '\U0001f525',
        logging.ERROR: '\u274c',
        logging.WARNING: '\u26a0\ufe0f\u0020',
        logging.INFO: '\u2139\ufe0f\u0020',
        logging.DEBUG: '\U0001f41b',
    }

    @property
    def _check_support(self):
        supported = sys.platform != 'win32' or 'ANSICON' in os.environ
        isatty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        return supported and isatty

    def __init__(self, *args, **kwargs):
        self._color = kwargs.pop('color', self._check_support)
        self._emoji = kwargs.pop('emoji', self._check_support)
        self._exclude = {'asctime', 'message'} | logging.makeLogRecord({}).__dict__.keys()
        super().__init__(*args, **kwargs)

    def format(self, record):
        if self._emoji:
            record.levelname = self._emoji_map.get(record.levelno, '\u2754')
        value = super().format(record)
        color = self._color and self._color_map.get(record.levelno)
        return f'\x1b[{color}m{value}\x1b[0m' if color else value

    def formatMessage(self, record):
        value = super().formatMessage(record)
        extra = {k: v for k, v in record.__dict__.items() if k not in self._exclude}
        if self._color and extra:
            extra = f'\x1b[2;3;37m{extra}\x1b[0m'
        return value + ' %s' % extra if extra else value

    def formatStack(self, value):
        value = super().formatStack(value)
        if self._color:
            value = value.replace('\n', '\x1b[0m\n\x1b[2;3;37m')
            return f'\x1b[2;3;37m{value}\x1b[0m'
        return value

    def formatException(self, value):
        value = super().formatException(value)
        if self._color:
            value = value.replace('\n', '\x1b[0m\n\x1b[2;3;37m')
            return f'\x1b[2;3;37m{value}\x1b[0m'
        return value


class ElasticsearchHandler(logging.Handler):

    def __init__(
        self,
        hosts=None,
        http_auth=None,
        use_ssl=False,
        verify_certs=True,
        index_name=None,
        extra_fields=None,
        raise_exceptions=False,
    ):
        super().__init__()
        hostname = socket.gethostname()

        self.hosts = hosts or [{'host': 'localhost', 'port': 9200}]
        self.http_auth = http_auth
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.index_name = '%s-{:%%Y.%%m.%%d}' % (index_name or 'unknown')
        self.extra_fields = {
            **{k: v for k, v in (extra_fields or {}).items() if v is not None},
            'host.name': hostname,
            'host.ip': socket.gethostbyname(hostname),
        }
        self.raise_exceptions = raise_exceptions

        self._client = None
        self._buffer = Queue()
        self._buffer_size = 1000
        self._flush_freq = 1.0
        self._timer = None
        self._serializer = Serializer()
        self._exclude_fields = {
            'args', 'created', 'exc_info', 'filename', 'levelno', 'module', 'msecs', 'msg', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName',
        }
        self._field_mapping = {
            'exc_text': 'log.traceback',
            'funcName': 'log.function',
            'levelname': 'log.level',
            'lineno': 'log.line',
            'name': 'log.name',
            'pathname': 'log.path',
            'stack_info': 'log.stack',
            # Work around log record attribute shadowing prevention:
            '_name': 'name',
        }

    @property
    def client(self):
        if self._client is None:
            self._client = elasticsearch.Elasticsearch(
                hosts=self.hosts,
                http_auth=self.http_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                connection_class=elasticsearch.RequestsHttpConnection,
                serializer=self._serializer,
            )
        return self._client

    def flush(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if self._buffer.qsize():
            index_name = self.index_name.format(datetime.datetime.utcnow())
            try:
                elasticsearch.helpers.bulk(
                    client=self.client,
                    actions=({'_index': index_name, '_type': 'log', '_source': record} for record in self._buffer.drain()),
                    stats_only=True,
                )
            except Exception as e:
                if self.raise_exceptions:
                    raise e

    def close(self):
        if self._timer is not None:
            self.flush()

    def emit(self, record):
        self.format(record)

        ts = datetime.datetime.utcfromtimestamp(record.created)
        ts = ts.replace(microsecond=ts.microsecond // 1000 * 1000, tzinfo=datetime.timezone.utc)

        self._buffer.put({
            **self.extra_fields,
            **{
                self._field_mapping.get(k, k): v for k, v in record.__dict__.items()
                if k not in self._exclude_fields and v is not None
            },
            'log.timestamp': ts.isoformat().replace('+00:00', 'Z'),
        })

        if self._buffer.qsize() >= self._buffer_size:
            self.flush()
        elif self._timer is None:
            self._timer = threading.Timer(self._flush_freq, self.flush)
            self._timer.setDaemon(True)
            self._timer.start()
