from celery import Celery

from qq.application import Application
from qq.plugins.settings import SettingsBasedPlugin


class CeleryPlugin(SettingsBasedPlugin):
    key = "celery"

    def __init__(
        self,
        celeryapp: Celery,
    ):
        super().__init__()
        self.celeryapp = celeryapp

    def start(self, application: Application):
        settings = self.get_my_settings(application)
        self.celeryapp.conf.update(settings)
