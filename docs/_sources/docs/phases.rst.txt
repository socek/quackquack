******
Phases
******

About
=====

The Application class was designed, so the configuration will always be run in
proper order. This needs to be sliced in phases, so the developer will know
in which order the plugin that was implemented will be executed.

Phase 0
=======

Before creating the Application instance, you can set something here, like
logging. But please don't use this phase very often. You should always try
to implement a plugin, because the plugins can use other plugins (for example
plugin for settings).

Phase 1 - creating Application instance
=======================================

This phase is not doing too much. It is executed when the Application instance
is created. It sets up the Application instance, so from now on, you can start
the Application. This is the ``__init__`` method of the Application class, so
if you want to extend this phase, you should overwrite this method.

Phase 2 - starting Application
==============================

This is where all the main stuff happen. This phase will start the plugins
(by start, I mean attach some data to the application). The plugins are started
in order of add order from ``create_plugins`` method. You should be careful about
the order.
For example, for minimal application, you should start Settings plugin at first,
and the logging after that, because logging is using the settings to configure
logger. This example is for default Settings and Logging plugins which comes
with the Sapp package.
You should also implement plugins in a way, so if you will have 2 Application
instances from the same class and you will start them in the same process with
the same arguments, you will have the same objects. It is because you can not be
sure when the Application will be started, and debbuing two different instances
of Application will be very hard if they are different.

From now on, you can use application as context manager.

Extending Phases
================

You can create your own phases on top of the existing ones. For example, if you
have Celery and Pyramid application, you would need to have pyramid phase. This
phase would execute tha Phase 2 at the beggining, and then run all the plugins,
with the new phase. So now, the Celery application would not start web plugins.

Context Phase Start
===================

This is where the application will be used as the context manager. This is the
enter step. Application will execute .start method on all the Plugins in order
of add order from ``create_plugins`` method. The responsibility of the plugins
is to add vars into the Application object.
For example, database plugin will start the session here in paste the session
into the application instance.

Context Phase End
=================

This is the exit step. Application will execute .exit method on all the Plugins in REVERSED
order of add order from ``create_plugins`` method.
For exampple, database plugin will start the session before another plugin will
us it. The exit will close th session.
So the database plun should start before other plugin and end after the other
plugin. That is why the Phase End will execute plugins in reversed order.
