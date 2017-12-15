from morfdict.models import Paths
from morfdict.models import StringDict

from sapp.plugin import Plugin


class SettingsPlugin(Plugin):
    """
    This class will generate settings for different startpoints. modulepath
    is a dotted path to the module with the settings startpoints (for example
    app.settings). Startpoint is a function which configure which modules to
    import during gathering settings.
    """

    def __init__(self, modulepath):
        self.modulepath = modulepath

    def start(self, configurator):
        startpoint = configurator.startpoint
        settings = self._gather_settings_for_startpoint(startpoint)
        self.push_settings_to_configurator(configurator, settings)

    def enter(self, application):
        application.settings = self.settings
        application.paths = self.paths

    def create_settings(self):
        return dict(settings=StringDict(), paths=Paths())

    def push_settings_to_configurator(self, configurator, settings):
        configurator.settings = settings['settings']
        configurator.paths = settings['paths']

    def _generate_settings(self):
        settings = self.create_settings()
        for fun in self.settings_funs:
            fun(**settings)
        return settings

    def _gather_settings_for_startpoint(self, startpoint):
        self.settings_funs = []
        module = self._import(self.modulepath)
        startpoint = getattr(module, startpoint)
        startpoint(self)
        return self._generate_settings()

    def append(self, modulepath, name='make_settings', silent_errors=False):
        try:
            module = self._import(modulepath)
            fun = getattr(module, name)
            self.settings_funs.append(fun)
        except ImportError:
            if silent_errors:
                return
            else:
                raise

    def _import(self, modulepath):
        return __import__(modulepath, globals(), locals(), [''])
