from qq.application import Application
from qq.injector import InjectApplicationContext
from qq.plugins import SettingsPlugin
from qq.plugins.settings import SettingsInjector


class AdadseApplication(Application):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin("qq.settings"))


app = AdadseApplication()
settings = SettingsInjector(app)


@InjectApplicationContext
def fun(something=10, sett=SettingsInjector(app)):
    print("end:", something, sett)


@InjectApplicationContext
def funer(something=10, sett=settings):
    print("Funer:", sett)
    raise RuntimeError("C")


print("D")
app.start("default")
print("E")

print(" --- FIRST --- ")
fun()

print("\n --- SECOND --- ")
fun(1, 2)

print("\n --- THIRD --- ")
fun(something=10, sett=20)


print("\n --- FOURTH --- ")
funer(something=10)
