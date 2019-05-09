from sapp.plugin import Plugin


class CeleryPlugin(Plugin):
    SETTINGS_KEY = "celery"

    def __init__(self, celeryapp):
        self.celeryapp = celeryapp

    def start(self, configurator):
        settings = configurator.settings[self.SETTINGS_KEY]
        self.celeryapp.conf.update(settings)
