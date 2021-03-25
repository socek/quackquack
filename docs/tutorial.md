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

You can also pass the context using decorator:

```python

from qq import InjectApplicationContext, SimpleInjector

app = MyApplication()

@InjectApplicationContext
def fun(something, settings = SimpleInjector(app, "settings")):
    print(settings)

fun("something")
```

This feature is a simple depndency injection, so if you like (for example in
tests) you can just pass the argument.

```python
# Remember to use keyword arguments here or else it will fail !!!
fun("something", settings=Mock())
```

# Creating Plugins

Power of the Quack Quack is in the plugins and how it is simple to create them.
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

    def start(self, application):
        """
        This method will be called at the start of the Application. It will be
        called only once and the result will be set in the Application.globals.
        """

    def enter(self, application):
        """
        This method will be called when the Application will be used as context
        manager. This is the enter phase. Result will be pasted in the Context
        dict.
        """

    def exit(self, application, exc_type, exc_value, traceback):
        """
        This method will be called when the Application will be used as context
        manager. This is the exit phase.
        """
```

# Extending the Application

If you would need to add another phase for plugins, you will need to add another
start method and just list thru all the plugins. For example, extension for
pyramid would look like this:

```python
class PyramidApplication(Application):
    PYRAMID_SETTINGS_KEY = "pyramid"
    _SETTINGS_KEY = SettingsPlugin.DEFAULT_KEY

    def make_wsgi_object(self, *args, **kwargs):
        """
        Configure application for web server and return pyramid's uwsgi
        application object.
        """
        pyramid = Configurator(*args, settings=self.settings, **kwargs)
        pyramid.registry["application"] = self
        self._start_pyramid_plugins(pyramid)
        return pyramid.make_wsgi_app()

    def _start_pyramid_plugins(self, pyramid: Configurator):
        for plugin in self.plugins.values():
            method = getattr(plugin, "start_pyramid", lambda x: x)
            method(pyramid)
```

In the `make_wsgi_object` method we are starting normal Sapp application and after
that we are configuring pyramid's application. Now we can start the plugins.
Please, notice that we are getting new method called "start_plugin" from the
plugins. This is because not all plugins are aware of our Pyramid extensions,
that is why the missing of the `start_plugin` method is a normal situation.
