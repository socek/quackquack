About
=====

`Documentation <https://qqpy.org/>`_


Overview
--------

This project aims to resolve problem of configuring an application, which needs to
have initialization step (for example: for gathering settings or establishing
connections) and use Python style code (context managers and decorators) to get
those data.

For example, normally you would need to use two separate mechanism for settings
in celery application and web application, because you should not use web
application startup process in the celery app. This package provide a solution
for this problem, by giving one simple and independent of other frameworks
mechanism to implement everywhere.

Quick Using Example
-------------------

To use Quack Quack you need to create the application class (inherited from
``qq.Application``\ ) in which you need to add plugins. After configuring, you need to "start"
the application. After that you can use the configurator as context manager.

.. code-block:: python

    from qq import Application, Context, InjectApplication, SimpleInjector
    from qq.plugins import SettingsPlugin
    from qq.plugins.types import Settings

    class MyApplication(Application):
        def create_plugins(self):
            self.plugins["settings"] = SettingsPlugin('settings')

    application = MyApplication()
    application.start('application')

    with Context(application) as ctx:
        print(ctx["settings"])

    @InjectApplication(application)
    def samplefun(settings: Settings = SimpleInjector("settings")):
        print(settings)



``context.settings`` in above example is variable made by the SettingsPlugin.
If you would like to know more, please go to the `Tutorial <https://qqpy.org/docs/tutorial.html>`_

Installation
------------

.. code-block:: bash

   pip install quackquack
