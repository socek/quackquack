# Table of Contents

0. [Go Home](../README.md)
1. [Configuration](#configuration)
2. [Starting](#starting)
3. [Using Context](#using-context)
4. [Using Decorator](#using-decorator)
5. [Creating Plugins](#creating-plugins)
6. [Extending Application](#extending-application)

# Configuration

First step using Quack Quack is to implement your own Application, which will be
inheriting from `qq.Application`. Bare Application almost does nothing, so it
needs plugins to work. In order to do that, you need to overwrite `create_plugins`
method and add some plugins. For the sake of tutorial, we just add one: Setting's Plugin

```python
from qq import Application
from qq.plugins import SettingsPlugin

class MyApplication(Application):
    def create_plugins(self):
        self.plugins["settings"] = SettingsPlugin('path.to.settings')

application = MyApplication()
```

Application instance should be created in some module as a global variable. This
object will be used in all of the places of the application. Making many
instances of the same class is possible, but it is a waste of resources, so
please avoid that.

# Starting

Starting is very important. This is the place, where the plugins will be
initalized. For example, for Logging plugin, this will be the place, where the
logging will start.

The start can be done only once, but it can be done for different processes (for
example for web application and celery worker), so we need to name it. This is
called "startpoint" and the default name is just "default".


```python
application = MyApplication()

def start_for_pyramid():
    application.start('pyramid')

def start_for_celery():
    application.start('celery')
```

# Using Context

After starting the application, we can use it as a context manager.

```python
from qq import Context

app = MyApplication()

with Context(app) as ctx:
    print(ctx["settings"])
```

This part shows how the plugin works in general. Every plugin returns simple
value (even if it's a dict) in context initialization. Initialization is made
only when the value is called by name.

Please, be aware, that you can nest the context managers. The context will be
generated once with the first `with` statement and ended with the same statement
ended.

```python
app = MyApplication()

with Context(app) as c1: # this is where context is initialized
    with app as c2:
        assert id(c1) == id(c2)
# this is where the context is ended/stopped
```

# Using Injectors

The most useful feature in QuackQuack are injectors. This functions are responsible
for injecting values from context into methods and functions. Injectors are passed
to the function as default arguments, so if you need to inject dependecy (for
example in tests), you can just pass the argument when calling. In order to
initialize the injectors, you need to to decorate function with
InitializeInjectors decorator.


```python

from qq import InitializeInjectors, SimpleInjector

app = MyApplication()

@InitializeInjectors
def fun(something, settings = SimpleInjector(app, "settings")):
    print(settings)

fun("something")
```

```python
# Remember to use keyword arguments here or else it will fail !!!
fun("something", settings=Mock())
```

# Creating Plugins

Quack Quack is designed in a way, that the core should be minimalistic, but the
plugins should be responsible for all the features (like settings). So
Only thing you need to do is inherit from `qq.Plugin`. This class should be self
explantory:

```python
class Plugin:
    def init(self, key: str):
        """
        Initialize the plguin during creating the plugins.
        key - key which is used in the Application.plugins dict for this plugin.
        """
        self.key = key

    def start(self, application: Application) -> Any:
        """
        This method will be called at the start of the Application. It will be
        called only once and the result will be set in the Application.globals.
        """

    def enter(self, application: Application) -> Any:
        """
        This method will be called when the Application will be used as context
        manager. This is the enter phase. Result will be pasted in the Context
        dict.
        """

    def exit(self, application: Application, exc_type, exc_value, traceback):
        """
        This method will be called when the Application will be used as context
        manager. This is the exit phase.
        """
```

