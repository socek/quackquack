from logging import getLogger

from sapp.configurator import Configurator
from tornado.ioloop import IOLoop


log = getLogger(__name__)


class TornadoConfigurator(Configurator):
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
