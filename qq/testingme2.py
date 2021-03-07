from qq import Application
from qq.context import Context
from qq.plugin import Plugin
from qq.plugins import SettingsPlugin


class NewPlugin(Plugin):
    """
    This class will generate settings for different startpoints. `modulepath`
    is a dotted path to the module with the settings startpoints. Startpoint is
    a function which will create proper settings and push them to configurator.
    """

    def enter(self, context):
        return {"new": context["settings"]}

    def exit(self, *args, **kwargs):
        print(f"Exiting NewPlugin")


class POCConfigurator(Application):
    def append_plugins(self):
        self.plugins["settings"] = SettingsPlugin("qq.settings")
        self.plugins["s2"] = NewPlugin()


app = POCConfigurator()
app.start()

print("zero")
with Context(app) as ctx:
    with Context(app) as ctx2:
        with Context(app) as ctx3:
            print(f"\ttwo: {ctx3['s2']}")
            print("\tthree")
print("Over")
