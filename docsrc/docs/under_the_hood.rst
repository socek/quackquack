**************
Models details
**************

Application
===========

Application class is very simple. The purpose of this class is to start all the
plugins. The two places where this is used are `create_plugins`  and `start`.

Create plugins
--------------

This is where you will added your plugins. Your application class should inherite
from the Application class and ovewrite the `create_plugins` method. In order to
add plugin you need to add plugin object to the `self.plugins` OrderedDict. Order
here is important, so you can not create a simple dict. As of Python 3.6, for the
CPython implementation of Python, dictionaries remember the order of items inserted,
but this is implementation detail, that is why the OrderDict is used here.

Dict keys of these plugins is used later on, so it is important not to ovewrite
already created plugin.

.. code-block:: python

    class MyApplication(Application):
        def create_plugins(self):
            self.plugins["settings"] = SettingsPlugin()

Plugins can return data in couple of places. Plugin's key is used to gather those
return values. For example, data from `start` method of the plugin can be found
in Application.globals.

.. code-block:: python

    app = MyApplication()
    app.start("startpoint")
    print(app.globals["settings"])

More about the places where the data of the plugins is stored can be found in
the :ref:`Plugins` section.


Application Start
-----------------

First step of the application should be starting (initializing) the Application
object by simply calling the `start` method.

.. code-block:: python

    app = MyApplication()
    app.start("startpoint")

`start` method needs at least one argument: startpoint. This is a name of the
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

Context
=======

.. _plugins:

Plugin
======

Starting
--------

This is the place, when the plugins are started (initialized). If there is a
need to do something only once (for example: read the settings), this is the
right place for this. Plugin classes have a method `start` where the
`Application.globals[key]`

Entering context
----------------

`Context[key]`

Exiting context
---------------

Injector
========
