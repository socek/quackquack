from celery import Celery

from sapp.application import Application
from sapp.plugins.settings import SettingsBasedPlugin
from sapp.plugins.settings import SettingsPlugin


class CeleryPlugin(SettingsBasedPlugin):
    DEFAULT_KEY = "celery"

    def __init__(
        self,
        celeryapp: Celery,
        key: str = None,
        settings_key: str = SettingsPlugin.DEFAULT_KEY,
    ):
        super().__init__(key, settings_key)
        self.celeryapp = celeryapp

    def start(self, application: Application):
        settings = self.get_my_settings(application)
        self.celeryapp.conf.update(settings)
