from logging.config import dictConfig

from qq.application import Application
from qq.plugins.settings import SettingsBasedPlugin


class LoggingPlugin(SettingsBasedPlugin):
    """
    Add logging configuration. Needs 'logging' value in settings.
    https://docs.python.org/3.6/library/logging.config.html#logging.config.dictConfig
    """

    key = "logging"

    def start(self, application: Application):
        dictConfig(self.get_my_settings(application))
