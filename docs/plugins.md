# Table of Contents

0. [Go Home](../README.md)
1. [Settings](#settings)
    * [History](#history)
    * [Implementing settings](#implementing-settings)
    * [Implementing paths settings](#implementing-paths-settings)
2. [Logging](#logging)
3. [JSON](#json)
4. [Redis](#redis)

# Settings

## History

Settings plugin was designed to make object of all the settings of the application,
which can be gather during the start of the application. There are many different
ways to achive this (Django uses simple python modules, Paster uses .ini file).
This mechanism needs to be simple as it can be, because we do not need anything
big here. We just want to get/set values depending on what part of the application
we want to use (different settings for web application, another for task workers
and totally different settings for tests). The advandtage of the Django's way
is that we can import modules on the fly, so we can decide which setting to use
depending on what do we want to use (run application or only tests). .ini files
does not gives us such flexability.

I do not like the Django way, because it is hard to make nice Python's code. In
many Django's setting files I have seen code, that would be not accetable in
other places due to the code smell (like dynamic imports, strange indentations).

## Implementing settings

Simple Python's dict should be enough to serve as settings container. It should
be generated in one place so reading the settings should be simple. Spliting code
in a parts(the database's settings will be in one place and the settings for web
application in another place) can be achived by using simple functions.

The only "magic" mechanism will be to choose proper settings for proper
"startpoint" (for example startpoint=webapp or startpoint=tests). All the
starpoints should prepere the same default options, which can change in the
future.

Example code:

```python
from myapp.application.settings.webapp import webapp_specific
from myapp.application.settings.tests import tests_specific


def _default():
    settings = {
        'project_name': 'example project name',
    }
    return settings

def webapp():
    settings = default()
    webapp_specific(settings)
    return settings

def tests():
    settings = default()
    webapp_specific(settings)
    tests_specific(settings)
    return settings
```

Here we have 2 startpoints: "webapp" and "tests". Now we need to add this plugin
to the configurator.

```python
class MyappConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin('myapp.application.settings'))
```

Now, we can create functions which will be execute by external mechanism (tests
function for example can be executed by pytest).

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
with ContextManager(app) as context:
    context.settings
```

Also, the settings can be retrived from the configurator.settings. This was
added because plugins will also need access to the settings.

## Implementing paths settings

If you wish to configure paths to settings, a simple dict can not be enough.
Our proposition is to have prefixed dict, in which you specify prefix once,
and all paths will be prefixed.

Example:

```python
from sapp.plugins.settings import PrefixedStringsDict

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
    settings['logging'] = {
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
            'mypet': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'qualname': 'mypet',
            },
            'waitress': {
                'level': 'ERROR',
                'handlers': ['console'],
            },
            'celery': {
                'handlers': ['console'],
                'level': 'ERROR',
            },
        }
    }
```

# JSON

This plugin is a stub. This stub makes `JSONEncoder` able to encode uuid objects
into json. To use it just add it to the Confiugrator:

```python

class MyConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(JsonPlugin())
```

# Redis

This plugin connects to the Redis database. In order to use it, you need to
add these settings:

```python
settings["redis:host"] = "redis"
settings["redis:port"] = 6379
settings["redis:db"] = 0
```

After that, you need add the plugin:

```python

class MyConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(RedisPlugin(ctx_key="context_key"))
```

The ctx_key is 'redis' by default. Now you can use it in your application:

```python
with ContextManager(app, 'context_key') as redis:
    print(redis)
```
