from logging.config import dictConfig

from sapp.plugin import Plugin


class LoggingPlugin(Plugin):
    """
    Add logging configuration. Needs 'logging' value in settings.
    https://docs.python.org/3.6/library/logging.config.html#logging.config.dictConfig
    """

    def start(self, configurator):
        dictConfig(configurator.settings['logging'])
