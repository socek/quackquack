from qapla.configurator import Configurator
from qapla.plugins.settings import SettingsPlugin


class MyConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin('qapla.mysettings'))


def elo():
    main = MyConfigurator()
    main.start_configurator('command')
    with main as app:
        print(app.settings)
