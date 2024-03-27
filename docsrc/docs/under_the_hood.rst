**************
Models details
**************

Application
===========

Application class is very simple. The purpose of that class is to start all the
plugins. The two places where this is used are `create_plugins`  and `start`.

Create plugins
--------------

This is where you will added your plugins. Your application class should inherite
from the Application class and overwrite the `create_plugins` method. In order to
add plugin you need to add plugin object to the `self.plugins` OrderedDict. Order
here is important, so you can not create a simple dict. As of Python 3.6, for the
CPython implementation of Python, dictionaries remember the order of items inserted,
but this is implementation detail, that is why the OrderDict is used here.

Dict keys of these plugins is used later on, so it is important not t o overwrite
already created plugin.

There are two types of plugins. One is the plugin that the name is harcoded, so
there will be only one instance of plugin. Those plugins needs to be inserted
by calling the `self.plugins`. Other plugins can have more instances (for example
if you need to have 2 databases )

.. code-block:: python

    class MyApplication(Application):
        def create_plugins(self):
            self.plugins(SettingsPlugin('path.to.settings'))

Plugins can return data in couple of places. Plugin's key is used to gather those
return values. For example, data from `start` method of the plugin can be found
in Application.globals.

.. code-block:: python

    app = MyApplication()
    app.start("startpoint")
    print(app.globals["settings"])

More about the places where the data of the plugins is stored can be found in
the Plugins section.


Application Start
-----------------

First step of the application should be starting (initializing) the Application
object by simply calling the `start` method.

.. code-block:: python

    app = MyApplication()
    app.start("startpoint")

`start` method has only one argument: startpoint. This is a name of the
"start place", which can be used later on. For example, if you have normal
startup and a test run, you can use different startpoint name. This startpoint
value will be used in :doc:`SettingsPlugin <settings>` in order to choose proper
function, so the settings for normal run and tests run will be different.

.. code-block:: python

    app = MyApplication()

    def normal_run():
        app.start("normal_run")

    def tests_run():
        app.start("tests_run")

`start` method can accept named arguments as well. These arguments will be stored
in the `Application.extra` dict for plugins to use.

.. code-block:: python

    app = MyApplication()
    app.start("normal_run", anothervalue=12)

    assert app.extra["anothervalue"] == 12


Plugin
======

Starting
--------

.. code-block:: python

    def start(self, application: Application) -> Any:

This is the place, when the plugins are started (initialized). If there is a
need to do something only once (for example: read the settings), this is the
right place for this. Plugin classes have a method `start`. Return object will
be put into `Application.globals[key]`.

Entering context
----------------

.. code-block:: python

    def enter(self, context: Context) -> Any:

This place will be run every time the application will be used as a context manager.
If you nest the `with` statement, this part will be executed only once. Return
of the `enter` method will be put into `Context[key]`.

Exiting context
---------------

.. code-block:: python

    def exit(self, context: Context, exc_type, exc_value, traceback):


As any other context manager, Plugin's class have also the `exit` method. This
is used to close connections or handle exceptions. Please, remember that `start`
is run in order of creating in `create_plugins`, but `exit` plugins is run in
reversed order.

Injectors and ApplicationInitializer
====================================

This feature is designed as a dependency injection. Injector is an object that
gets a context and return something. This function needs to be decorated with
`Injector` function.

Example:

.. code-block:: python

    from qq.injectors import ContextInicjator

    class SimpleInicjator(ContextInicjator):
        def start(self):
            return self.context[self.key]

In order to use the `injector`, it needs to be provided as a default var in a
function. Also, the `ApplicationInitializer` needs to be used for that function.
The `ApplicationInitializer` is responsible for "starting" the injectors.

Example:

.. code-block:: python

    from qq.injectors import ArgsInjector

    @ArgsInjector(application, {"settings": SimpleInicjator("settings")})
    def fun(settings):
        ...


The `ApplicationInitializer` decorator is used to initialize the injectors with
provided application. There is no need of using `Application` as a context manager
here,
the function will be used under a with statement. For example, above code can be
Implemented like this:

.. code-block:: python

    from qq.context import Context

    def fun(settings):
        ...

    with Context(application) as context:
        settings = context["settings"]
        fun(settings)

The advandtage of the injectors is that you do not need to pass the context value
everywhere or use the `with` statement. So it mitigate the boilerplate. Also,
you can pass arguments instead of default values in functions. This dependency
injection is very helpful in implementation of tests.

Example:

.. code-block:: python

    @ArgsInjector(application, {"settings": SimpleInicjator("settings")})
    def fun(settings):
        return settings

    def test_flow():
        mock = MagicMock()
        assert fun(mock) == mock


The `ApplicationInitializer` function can overwrite the application var, so you
can create a function with injectors in a library, but add the application var
later.

Example:

.. code-block:: python

    from qq import ApplicationInitializer

    @ArgsInjector(None, {"settings": SimpleInicjator("settings")})
    def fun(settings):
        ...

    fun2 = ArgsInjector(application)(fun)

The `ApplicationInitializer` will overwrite the `application` value in all injectors.
If those injectors would have it's own injectors in the arguments, those injectors
will have the new `application` value as well.

