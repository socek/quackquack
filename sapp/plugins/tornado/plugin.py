from tornado.httpserver import HTTPServer
from tornado.log import enable_pretty_logging
from tornado.web import Application as Tornado


class TornadoPlugin(object):
    def start(self, configurator):
        debug = configurator.settings["debug"]
        enable_pretty_logging()
        configurator.tornado = Tornado(debug=debug, serve_traceback=True)
        configurator._http_server = HTTPServer(configurator.tornado)

    def enter(self, context):
        pass

    def exit(self, *args, **kwargs):
        pass
