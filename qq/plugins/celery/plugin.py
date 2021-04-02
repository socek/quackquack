from celery import Celery

from qq.application import Application
from qq.plugins.settings import SettingsBasedPlugin
from qq.plugins.settings import SettingsPlugin


class CeleryPlugin(SettingsBasedPlugin):
    DEFAULT_KEY = "celery"

    def __init__(
        self,
        celeryapp: Celery,
        settings_key: str = SettingsPlugin.DEFAULT_KEY,
    ):
        super().__init__(settings_key)
        self.celeryapp = celeryapp

    def start(self, application: Application):
        settings = self.get_my_settings(application)
        self.celeryapp.conf.update(settings)
