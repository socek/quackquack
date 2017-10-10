from morfdict import Factory


class SettingsFactory(object):
    """
    This class will generate settings for different endpoints.
    SettingsFactory.module is a dotted prefix for the settings (for example app.settings).
    All endpoints will import the default module. After that the endpoint will try
    to import the rest modules provided in the list. If it is with `True`, the
    Factory will raise an error (FileNotFound). Otherwise the error will not be raised.
    """
    ENDPOINTS = {
        'uwsgi': [('local', False)],
        'tests': [('tests', False), ('local', False)],
        'shell': [('shell', False), ('local_shell', False)],
        'command': [('command', False), ('local_command', False)],
    }

    def __init__(self, module, settings=None, paths=None):
        self.module = module
        self.settings = settings or {}
        self.paths = paths or {}

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
