from collections import namedtuple

from morfdict import Factory

SettingsModule = namedtuple('SettingsModule', ['name', 'is_needed'])


class SettingsFactory(object):
    """
    This class will generate settings for different endpoints.
    SettingsFactory.module is a dotted prefix for the settings (for example app.settings).
    All endpoints will import the default module. After that the endpoint will try
    to import the rest modules provided in the list. If it is with `True`, the
    Factory will raise an error (FileNotFound). Otherwise the error will not be raised.
    """
    ENDPOINTS = {
        'uwsgi': [
            SettingsModule('local', False)],
        'tests': [
            SettingsModule('tests', False),
            SettingsModule('local', False)],
        'shell': [
            SettingsModule('shell', False),
            SettingsModule('local_shell', False),
            SettingsModule('local', False)],
        'command': [
            SettingsModule('command', False),
            SettingsModule('local_command', False),
            SettingsModule('local', False)],
    }

    def __init__(self, module, settings=None):
        self.module = module
        self.settings = settings or {}

    def get_for(self, endpoint):
        files = self.ENDPOINTS[endpoint]
        return self._generate_settings(files)

    def _generate_settings(self, files=None):
        files = files or []
        factory = Factory(self.module)
        settings, paths = factory.make_settings(
            settings=self.settings,
            additional_modules=files,
        )
        return settings, paths
