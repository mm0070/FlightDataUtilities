import datetime
import logging
import queue
import socket
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
