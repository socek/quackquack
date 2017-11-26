from logging.config import dictConfig

from qapla.plugin import Plugin


class LoggingPlugin(Plugin):
    """
    Add logging configuration. Needs 'logging' value in settings.
    https://docs.python.org/3.6/library/logging.config.html#logging.config.dictConfig
    """

    def start_plugin(self, configurator):
        self.configurator = configurator

    def start_web_plugin(self, pyramid):
        dictConfig(self.configurator.settings['logging'])
