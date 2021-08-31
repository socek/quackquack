
Quack Quack
===========

If it quacks like a quack, then it's a Quack Quack.
Version: 1.0.4

Table of Contents
=================


#. `Overview <#overview>`_
#. `Quick Using Guide <#quick-using-guide>`_
#. `Installation <#installation>`_
#. `Tutorial <docs/tutorial.md>`_

   * `Configuration <docs/tutorial.md#configuration>`_
   * `Starting <docs/tutorial.md#starting>`_
   * `Using Context <docs/tutorial.md#using-context>`_
   * `Using Injectors <docs/tutorial.md#using-injectors>`_
   * `Creating Plugins <docs/tutorial.md#creating-plugins>`_

#. `Plugins <docs/plugins.md>`_

   * `Settings <docs/plugins.md#settings>`_
   * `Logging <docs/plugins.md#logging>`_
   * `Redis <docs/plugins.md#redis>`_
   * `Pyramid Plugin <docs/pyramid.md>`_
   * `Sqlalchemy Plugin <docs/sqlalchemy.md>`_
   * `Json Plugin <docs/json.md>`_

#. `Phases <docs/phases.md>`_

   * `About Phases <docs/phases.md#about-phases>`_
   * `Phase 0 <docs/phases.md#phase-0>`_
   * `Phase 1 - creating Configurator instance <docs/phases.md#phase-1---creating-configurator-instance>`_
   * `Phase 2 - starting Configurator <docs/phases.md#phase-2---starting-configurator>`_
   * `Extending Phases <#extending-phases>`_
   * `Application Phase Start <docs/phases.md#application-phase-start>`_
   * `Application Phase End <docs/phases.md#application-phase-end>`_

#. More info

   * `Changelog <docs/CHANGELOG.md>`_

#. `Example <example/readme.md>`_

Overview
========

This project aims to resolve problem of configuring an application, which needs to
have initialization step (for example: for gathering settings or establishing
connections) and use Python style code (context managers and decorators) to get
those data.

For example, normally you would need to use two separate mechanism for settings
in celery application and web application, because you should not use web
application startup process in the celery app. This package provide a solution
for this problem, by giving one simple and independent of other frameworks
mechanism to implement everywhere.

Quick Using Guide
=================

To use Quack Quack you need to create the application class (inherited from
``qq.Application``\ ) in which you need to add plugins. After configuring, you need to "start"
the application. After that you can use the configurator as context manager.

.. code-block:: python

   from qq import Application, Context
   from qq.plugins import SettingsPlugin

   class MyApplication(Application):
       def create_plugins(self):
           self.plugins["settings"] = SettingsPlugin('settings')

   application = MyApplication()
   application.start('application')

   with Context(application) as ctx:
       print(ctx["settings"])

``context.settings`` in above example is variable made by the SettingsPlugin.
If you would like to know more, please go to the `Tutorial <docs/tutorial.md>`_

Installation
============

.. code-block:: bash

   pip install quackquack
