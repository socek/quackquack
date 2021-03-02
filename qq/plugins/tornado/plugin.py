from tornado.httpserver import HTTPServer
from tornado.log import enable_pretty_logging
from tornado.web import Application as Tornado

from qq.application import Application
from qq.plugins.settings import SettingsBasedPlugin

DEBUG_KEY = "debug"
SERVE_TRACEBACK_KEY = "serve_traceback"


class TornadoPlugin(SettingsBasedPlugin):
    DEFAULT_KEY = "tornado"

    def start(self, application: Application):
        settings = self.get_my_settings(application)
        debug = settings.get(DEBUG_KEY, False)
        serve_traceback = settings.get(SERVE_TRACEBACK_KEY, False)
        enable_pretty_logging()
        tornado = Tornado(debug=debug, serve_traceback=serve_traceback)

        return {
            "tornado": tornado,
            "http_server": HTTPServer(tornado),
        }
