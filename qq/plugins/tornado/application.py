from logging import getLogger

from tornado.ioloop import IOLoop

from qq.application import Application

log = getLogger(__name__)


class TornadoApplication(Application):
    def __init__(self):
        super().__init__()
        self.io_loop = IOLoop.instance()

    def start_tornado_loop(self):
        self._http_server.listen(self.settings["tornado_port"])
        try:
            log.info("Starting application...")
            self.io_loop.start()
        except KeyboardInterrupt:
            self.io_loop.stop()
