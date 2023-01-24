Tutorial
========

Configuration
-------------

First step in using Quack Quack is to implement your own Application, which should be
inheriting from ``qq.Application``. Bare Application almost does nothing, so it
needs plugins to work. In order to do that, you need to overwrite ``create_plugins``
method and add some plugins. For the sake of tutorial, we just add one: Setting's Plugin

.. code-block:: python

   from qq import Application
   from qq.plugins import SettingsPlugin

   class MyApplication(Application):
       def create_plugins(self):
           self.plugins(SettingsPlugin('path.to.settings'))

   application = MyApplication()

Application instance should be created in some module as a global variable. This
object will be used in all of the places of the application. Making many
instances of the same class is possible, but it is a waste of resources, so
please avoid that.

Starting
--------

Starting is very important. This is the place, where the plugins will be
initalized. For example, for Logging plugin, this will be the place, where the
logging will start.

The start can be done only once, but it can be done for different processes (for
example for web application and celery worker), so we can switch some configuration
between application's processes. For example, one start can be for normal run,
second for the tests, with mocked database. First we need to name the starts.
Those are called "startpoints" and the default name is just "default".

.. code-block:: python

   application = MyApplication()

   def start_for_pyramid():
       application.start('pyramid')

    def start_for_celery():
       application.start('celery')

    def start_for_tests():
        application.start('tests')

Those start points are used mainly by settings plugin, so the settings can be
switchable. Example for above start points:

.. code-block:: python

   def default():
        return {"default": 1}

    def pyramid():
        settings = default()
        settings["pyramid"] = True
        return settings

    def celery():
        settings = default()
        settings["celery"] = 'yes'

    def tests():
        settings = default()
        settings["tests"] = True is True

Using Context
-------------

After starting the application, we can use it as a context manager.

.. code-block:: python

   from qq import Context

   app = MyApplication()
   app.start()

   with Context(app) as ctx:
       print(ctx["settings"])

This part shows how the plugin works in general. Every plugin returns simple
value (even if it's a dict) in context initialization. Initialization is made
only when the value is called by name (so you can call it lazy initialization).

Please, be aware, that you can nest the context managers. The context will be
generated once with the first ``with`` statement and ended with the same statement
ended.

.. code-block:: python

   app = MyApplication()
   app.start("pyramid")

   with Context(app) as c1: # this is where context is initialized
       with Context(app) as c2:
           assert id(c1) == id(c2)
   # this is where the context is ended/stopped

Using Injectors and dependency injection
----------------------------------------

The most useful feature in QuackQuack are injectors. This objects are responsible
for injecting values from context into methods and functions. Injectors are passed
to the function as default arguments, so if you need to inject dependecy (for
example in tests), you can just pass the argument when calling. In order to
initialize the injectors, you need to to decorate function with
ApplicationInitializer decorator.

.. code-block:: python

    from qq import Application
    from qq import ApplicationInitializer
    from qq import SimpleInjector
    from qq.plugins import SettingsPlugin


    class MyApplication(Application):
        def create_plugins(self):
            self.plugins(SettingsPlugin("settings"))


    application = MyApplication()
    app = ApplicationInitializer(application)


    @app
    def fun(something, settings=SimpleInjector("settings")):
        print(something, settings)


    application.start()
    fun("something")

.. code-block:: python

   from unittest.mock import MagicMock
   fun("something", MagicMock())
   fun("something", settings=MagicMock())

If the method is a coroutine, you don't need to do nothing. It will work the same.


.. code-block:: python

    from asyncio import run

    from qq import Application
    from qq import ApplicationInitializer
    from qq import SimpleInjector
    from qq.plugins import SettingsPlugin


    class MyApplication(Application):
        def create_plugins(self):
            self.plugins(SettingsPlugin("settings"))


    application = MyApplication()
    app = ApplicationInitializer(application)


    @app
    async def fun(something, settings=SimpleInjector("settings")):
        print(something, settings)


    application.start()
    run(fun('something'))


Creating Plugins
----------------

Quack Quack is designed in a way, that the core should be minimalistic, but the
plugins should be responsible for all the features (like settings plugin). So the
only thing you need to do is inherit from ``qq.Plugin``. This class should be self
explantory:

.. code-block:: python

    from typing import Any

    from qq.context import Context
    from qq.types import Application
    from qq.types import Plugin as PluginType
    from qq.types import PluginKey


    class Plugin(PluginType):
        key: PluginKey = None

        def init(self, key: PluginKey):
            """
            Initialize the plugin during creation.
            key - key which is used in the Application.plugins dict for this plugin.
            """
            self.key = key

        def start(self, application: Application) -> Any:
            """
            This method will be called at the start of the Application. It will be
            called only once and the result will be set in the Application.globals.
            """

        def enter(self, context: Context) -> Any:
            """
            This method will be called when the Application will be used as context
            manager, but only when the plugin will be called. This is the enter phase.
            Result will be set in the Context dict with the self.key as the key in
            that dict.
            """

        def exit(self, context: Context, exc_type, exc_value, traceback):
            """
            This method will be called when the Application will be used as context
            manager. This is the exit phase.
            """


