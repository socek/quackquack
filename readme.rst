About
=====

`Documentation <https://qqpy.org/>`_


Overview
--------

This project aims to resolve problem of configuring an application, which needs to
have initialization step (for example: for gathering settings or establishing
connections) and use Python style code (context managers and decorators) with
dependency injection to get those data.

For example, normally you would need to use two separate mechanism for connection
to the database (one for web, and one for celery). Mostly it uses the web framework
configuration, to use in the celery code. It is fine, until a third sub-application
arrives. Or you have many microservices, where web frameworks are different
depending on the microservice purpose.

Second goal was to make synchronized code without any globals or magic. That is
why using Quack Quack you know when the application is initialized (started),
or where to look for code you are using.

In order to use QQ, you don't need to use hacks in some starting files, like
importing something from django, starting the application, and the import the
rest.

Quick Using Example
-------------------

To use Quack Quack you need to create the application class (inherited from
``qq.Application``\ ) in which you need to add plugins. After configuring, you
need to "start" (initialize)
the application. After that you can use the application as context manager.
Also, you can make simple decorator, so you can use injectors (dependency
injection) in function's arguments.

.. code-block:: python

    from qq import Application
    from qq import ApplicationInitializer
    from qq import Context
    from qq import SimpleInjector
    from qq.plugins import SettingsPlugin
    from qq.plugins.types import Settings


    class MyApplication(Application):
        def create_plugins(self):
            self.plugins["settings"] = SettingsPlugin("settings")


    application = MyApplication()
    application.start("application")

    with Context(application) as ctx:
        print(ctx["settings"])

    app = ApplicationInitializer(application)


    @app
    def samplefun(settings: Settings = SimpleInjector("settings")):
        print(settings)


    samplefun()
    samplefun({"info": "fake settings"})  # dependency injection !!


``context["settings"]`` in above example, is a variable made by the SettingsPlugin.
If you would like to know more, please go to the `Tutorial <docs/tutorial.md>`_

Installation
------------

.. code-block:: bash

   pip install quackquack
