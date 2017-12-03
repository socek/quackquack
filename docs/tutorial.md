# Table of Contents

0. [Go Home](../README.md)
1. [Configuration](#configuration)
2. [Starting](#starting)
3. [Creating Plugins](#creating-plugins)
4. [Extending Configurator](#extending-configurator)

# Configuration

First step in using Sapp is to make your own Configurator, which will be
inherited from `sapp.Configurator`. There you would overwrite `append_plugins`
method, whis is a place to append the plugins.

```python
from sapp.configurator import Configurator
from sapp.plugins import SettingsPlugin

class MyConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin('path.to.settings'))

main = MyConfigurator()
```

There is no need to do more with the configurator at this point. If you wish to
extend the Configurator class, please see the [Extending Configurator](#extending-configurator)
section below.

Configurator object should be created in some module as an global object. This
object will be used in all of the places of the application (it should not be
created in many places!).

# Starting

Starting is very important. This is the place, where the plugins will be
initalized. For example, for Logging plugin, this will be the place, where the
logging will start.

The start can be done only once, but there can be many endpoints in where you
can do it. For example, you can make start for web application and for celery
application. This two starts can be different, but they can use one Configurator
object.

```python
main = MyConfigurator()

def start_for_pyramid():
    main.start('pyramid')

def start_for_celery():
    main.start('celery')
```

# Creating Plugins

Power of the Sapp is in the plugins and how it is simple to create them. Only
thing you need to do is inherit from `sapp.Plugin`. This class should be self
explantory:

```python
class Plugin(object):
    def start(self, configurator):
        """
        This method will be called at the start of the Configurator. It will be
        called only once per process start. configurator is an object where all
        the configuratation is stored.
        """

    def enter(self, application):
        """
        This method will be called when the Configurator will be used as context
        manager. This is the enter phase.
        """

    def exit(self, application, exc_type, exc_value, traceback):
        """
        This method will be called when the Configurator will be used as context
        manager. This is the exit phase.
        """
```

# Extending Configurator

If you would need to add another phase for plugins, you will need to add another
start method and just list thru all the plugins. For example, extension for
pyramid would look like this:

```python
class ConfiguratorWithPyramid(Configurator):
    def start_pyramid_plugins(self, pyramid):
        for plugin in self.plugins:
            method = getattr(plugin, 'start_pyramid', lambda x: x)
            method(pyramid)

    def start_pyramid(self, *args, **kwargs):
        self.start('pyramid')

        pyramid = PyramidConfigurator(*args, **kwargs)
        self.start_pyramid_plugins(pyramid)
        return pyramid.make_wsgi_app()
```

In the `start_pyramid` method we are starting normal Sapp application and after
that we are configuring pyramid's configurator. Now we can start the plugins.
Please, notice that we are getting new method called "start_pyramid" from the
plugins. This is because not all plugins are aware of our Pyramid extensions,
that is why the missing of the `start_pyramid` method is a normal situation.
