# Table of Contents

0. [Go Home](../README.md)
1. [Settings](#settings)
    * [History](#history_and_concept)
    * [Implementing settings](#implementing-settings)
    * [Other plugins and settings](#other-plugins-and-settings)
    * [Implementing paths settings](#implementing-paths-settings)
2. [Logging](#logging)
3. [Redis](#redis)
4. [Pyramid Plugin](pyramid.md)
5. [Sqlalchemy Plugin](sqlalchemy.md)
6. [Json Plugin](json.md)

# Settings

## History and concept

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

## Implementing settings

Simple Python's dict should be enough to serve as settings container. It should
be generated in one place so reading the settings will be simple. Spliting code
in a parts(the database's settings will be in one place and the settings for web
application in another place) can be achived by using simple functions.

The only "magic" mechanism will be to choose proper settings for proper
"startpoint" (for example startpoint="webapp" or startpoint="tests"). All the
starpoints should prepere the same default options, which can be changed in the
future.

Example code:

```python
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
```

Here we have 2 startpoints: "webapp" and "tests". Now we need to add this plugin
to the configurator.

```python
from qq import Application
from qq.plugins import SettingsPlugin

class Myapp(Application):
    def create_plugins(self):
        self.plugins[SettingsPlugin.DEFAULT_KEY] = SettingsPlugin('path.to.settings')
```

Now, we can create functions which will be execute by external mechanism (tests
function for example can be executed by pytest).

`create_wsgi_app` method is something from Pyramid plugin. Please go there for
more info.

```python
from myapp import app


def uwsgi():
    app.start('webapp')
    return app.create_wsgi_app()


def tests():
    app.start('tests')
```

For getting values from settings, you can get if from the context:

```python
from qq import Context
with Context(app) as context:
    context[SettingsPlugin.DEFAULT_KEY]
```

Also, the settings can be retrived from the application.globals["settings"]. This was
added because plugins will also need access to the settings.

## Other plugins and settings

Settings should be divided into dicts, so every plugin should have it's own dict
for settings. For example, if you have 3 plugins (and Settings plugin) looking
like this:

```python

class Myapp(Application):
    def create_plugins(self):
        self.plugins["settings"] = SettingsPlugin('path.to.settings')
        self.plugins["sql"] = SqlAlchemy()
        self.plugins["redis"] = RedisPlugin()
        self.plugins["secondredis"] = RedisPlugin()
        self.plugins[CUSTOM_PLUGIN_KEY] = CustomPlugin()
```

In settings module it should look like this (using the same keys as the plugin):

```python

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
```

Implementing custom plugins with settings is also simple. You need to inherit from
`SettingsBasedPlugin` and use `get_my_settings` method to get the proper settings.

```python

from qq.plugins.settings import SettingsBasedPlugin

class CustomPlugin(SettingsBasedPlugin):

    def start(self, application: Application) -> Any:
        assert self.get_my_settings(application) == {"options": "something"}

    def enter(self, context: Context) -> Any:
        assert self.get_my_settings(context) == {"options": "something"}
```

## Implementing paths settings

If you wish to configure paths to settings, a simple dict can not be enough.
Our proposition is to have prefixed dict, in which you specify prefix once,
and all paths will be prefixed.

Example:

```python
from qq.plugins.settings import PrefixedStringsDict

def default():
    paths = PrefixedStringsDict('/code/')
    paths['app.ini'] = 'app.ini'
    assert paths['app.ini'] == '/code/app.ini'

    settings = {
        'paths': paths,
    }
    return settings
```

# Logging

Logging is a very simple plugin. It uses `logging.config.dictConfig` from the
standard python's library. Plugin will just get the settings['logging'] value
and push it to the dictConfig. The logging will start when the Configurator
instance will be started.

Exapmle of the configuration:
```python
def logging(settings):
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'generic': {
                'format':
                '%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s',
            },
        },
        'handlers': {
            'console': {
                'level': "DEBUG",
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
            },
        },
        'loggers': {
            '': {
                'level': 'DEBUG',
                'handlers': [],
            },
            'sqlalchemy': {
                'level': 'ERROR',
                'handlers': ['console'],
                'qualname': 'sqlalchemy.engine',
            },
            'alembic': {
                'level': 'ERROR',
                'handlers': ['console'],
                'qualname': 'alembic',
            },
            'celery': {
                'handlers': ['console'],
                'level': 'ERROR',
            },
            'myapp': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'qualname': 'myapp',
            },
        }
    }
```

# Redis

This plugin connects to the Redis database. It will return `redis.Redis` connection
to the context.

In order to use it, you need to add these settings:

```python
def redis(settings):
    return {
        "host": "redis",
        "port": 6379,
        "db": 0,
    }
```

Second step is to add the plugin, like any other plugins:

```python

class MyApplication(Application):
    def create_plugins(self):
        self.plugins[REDIS_PLUGIN_KEY] = RedisPlugin()
```

The ctx_key is 'redis' by default. Now you can use it in your application:

```python
with Context(app) as ctx:
    print(ctx[REDIS_PLUGIN_KEY])
    assert type(ctx[REDIS_PLUGIN_KEY]) == redis.Redis
```
