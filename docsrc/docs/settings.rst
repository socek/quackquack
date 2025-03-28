Settings
========

History and concept
-------------------

Settings plugin was designed to make object of all the settings of the application,
which can be gather during the start of the application. There are many different
ways to achive this (Django uses simple python modules, Paster uses .ini file).
This mechanism needs to be simple as it can be, because we do not need anything
complicated here. We just want to get/set values depending on what part of the application
we want to use (different settings for web application, another for task workers
and totally different settings for tests). The advandtage of the Django's way
is that we can import modules on the fly, so we can decide which setting to use
depending on what do we want to use (run application or only tests). .ini files
does not gives us such flexability.

I do not like the Django way, because it is hard to make nice Python's code. In
many Django's setting files I have seen code, that would be not accetable in
other places due to the code smell (like dynamic imports, strange indentations
and so on).

Implementing settings
---------------------

Simple Python's dict should be enough to serve as settings container. It should
be generated in one place so reading the settings will be simple. Spliting code
in a parts(the database's settings will be in one place and the settings for web
application in another place) can be achived by using simple functions.

The only "magic" mechanism will be to choose proper settings for proper
"startpoint" (for example startpoint="webapp" or startpoint="tests"). All the
starpoints should prepere the same default options, which can be changed in the
future.

Example code:

.. code-block:: python

   from myapp.application.settings.webapp import webapp_specific
   from myapp.application.settings.tests import tests_specific
   from qq.plugins.types import Settings


   def _default() -> Settings:
       settings = {
           'project_name': 'example project name',
           "database": database(),
       }
       return settings

   def database() -> Settings:
       return {
           "db": "something",
       }

   def webapp() -> Settings:
       settings = _default()
       webapp_specific(settings)
       return settings

   def tests() -> Settings:
       settings = _default()
       webapp_specific(settings)
       tests_specific(settings)
       return settings


Here we have 2 startpoints: "webapp" and "tests". Now we need to add this plugin
to the configurator.

.. code-block:: python

   from qq import Application
   from qq.plugins import SettingsPlugin

   class Myapp(Application):
       def create_plugins(self):
           self.plugins(SettingsPlugin('path.to.settings'))


Now, we can create functions which will be execute by external mechanism (tests
function for example can be executed by pytest).

``create_wsgi_app`` method is something from Pyramid plugin. Please go there for
more info.

.. code-block:: python

   from myapp import app


   def uwsgi():
       app.start('webapp')
       return app.create_wsgi_app()


   def tests():
       app.start('tests')


For getting values from settings, you can get if from the context:

.. code-block:: python

   from qq import Context
   with Context(app) as context:
       context[SettingsPlugin.key]


Also, the settings can be retrived from the application.globals["settings"]. This was
added because plugins will also need access to the settings.

Other plugins that uses settings
--------------------------------

Settings should be divided into dicts, so every plugin should have it's own dict
for settings. For example, if you have 3 plugins (and Settings plugin) looking
like this:

.. code-block:: python


   class Myapp(Application):
       def create_plugins(self):
           self.plugins(SettingsPlugin('path.to.settings'))
           self.plugins["sql"] = SqlAlchemy()
           self.plugins["redis"] = RedisPlugin()
           self.plugins["secondredis"] = RedisPlugin()
           self.plugins[CUSTOM_PLUGIN_KEY] = CustomPlugin()


In settings module it should look like this (using the same keys as the plugin):

.. code-block:: python


   def default():
       settings = {
           "project_name": "example project name",
       }
       settings["sql"] = sqlsettings()
       settings["redis"] = redissettings(settings)
       settings["secondredis"] = secondredissettings(settings)
       settings[CUSTOM_PLUGIN_KEY] = customsettings()
       return settings

   def sqlsettings():
       return {"host": "localhost"}

   def redissettings(settings):
       return {"host": "localhost", "db": 1}

   def secondredissettings(settings):
       return {"host": "localhost", "db": 2}

   def customsettings():
       return {"options": "something"}


Implementing custom plugins with settings is also simple. You need to inherit from
``SettingsBasedPlugin`` and use ``get_my_settings`` method to get the proper settings.

.. code-block:: python


   from qq.plugins.settings import SettingsBasedPlugin

   class CustomPlugin(SettingsBasedPlugin):

       def start(self, application: Application) -> Any:
           assert self.get_my_settings(application) == {"options": "something"}

       def enter(self, context: Context) -> Any:
           assert self.get_my_settings(context) == {"options": "something"}


Settings Injector
-----------------

Most of the cases the developer do not need access to all of the settings, but
rather settings depending on the module of the code it is using. So, you can
use the SettingsInjector, like this:

.. code-block:: python

    from qq.injectors import SetApplication
    from qq.injectors import SetInicjator
    from qq.plugins.settings import SettingsInicjator

    @SetApplication(app)
    @SetInicjator("jwt_settings", SettingsInjector("jwt"))
    def somemethod(argument, jwt_settings):
        ...


But, you can always get the all settings if you want:

.. code-block:: python

    from qq.injectors import SetApplication
    from qq.injectors import SetInicjator
    from qq.injectors import ContextInicjator

    @SetApplication(app)
    @SetInicjator("all_settings", ContextInicjator("settings"))
    def somemethod(argument, all_settings):
        ...

