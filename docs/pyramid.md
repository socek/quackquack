# Pyramid Plugin

0. [Go Home](../README.md)
1. [About](#about)
2. [Extended Configurator](#extended-configurator)
    * [Implement Configurator](#implement-configurator)
    * [Implement Startpoint](#implement-startpoint)
    * [Configuring Egg](#configuring-egg)
    * [Configuring Paster](#configuring-paster)
    * [Starting development server](#starting-development-server)
    * [Starting uwsgi server](#starting-uwsgi-server)
    * [Creating Plugins for Pyramid](#creating-plugins-for-pyramid)
3. [Routing Wrapper](#routing-wrapper)
4. [Controllers](#controllers)
5. [BaseWebTestFixture](#basewebtestfixture)

# About

Pyramid Plugin is a set of couple of features:

- [Extended Configurator](#extended-configurator) and plugins - allows to creat
    wsgi object for uwsgi
- [Routing Wrapper](#routing-wrapper) - allows to get view value from class
    variables
- [Controllers](#controllers) - controller classes with some neat features and
    fixtures for pytest
- [BaseWebTestFixture](#basewebtestfixture) - fixtures for pytest to use webtest

All these features can be used separately.

# Extended Configurator

Pyramid Framework gives us possibility to create wsgi application, which can be
used by the uwsgi process. Pyramid is using Paster to configure. This means we
need to configure some stuff in the Paster/Pyramid way.

## Implement Configurator

Implementing the Configurator is pretty simple. Only thing needed to be done is
to inherited your Configurator from `ConfiguratorWithPyramid` insted of the
normal configurator. The new Configurator will be responsible for running
Pyramid's plugins.

For example, we will add SettingsPlugin fro Sapp and RoutingPlugin fro Sapp's
Pyramid.

```python
from sapp.plugins.pyramid.configurator import ConfiguratorWithPyramid
from sapp.plugins.pyramid.plugins import RoutingPlugin

from myapp.application.routing import MyappRouting

class MyappConfigurator(ConfiguratorWithPyramid):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin('myapp.application.settings'))
        self.add_plugin(RoutingPlugin(MyappRouting))
```
As you can see, you can use normal plugins along with the Pyramid's specifyc
ones. Mor about plugins can be found [here](#creating-plugins)

## Implement Startpoint

Second step is to create a startpoint. It needs to be a function which will
return an wsgi object, which can be used by uwsgi oraz paster. In order to do
that we need to start the Configurator.

Example:

```python
from myapp import app


def wsgi(settings):
    app.start('pyramid')
    return app.make_wsgi_object()
```

The settings argument is not used here. It is something that will be passed to
the function by the uwsgi or paster, but Sapp Settings does not use it at all.

## Configuring Egg

You need to have proper setup.py which will create an egg for us. Creating
proper setup.py is described in the Python's Documentation
[here](https://docs.python.org/3.6/distutils/setupscript.html).

In the setup method you need yo add this lines:

```python
entry_points={
    'paste.app_factory': ['main = myapp.startpoints:wsgi'],
}
```

Of course, if you have entry_points already, you can extend it.
`paste.app_factory` is name of the value which will be read by the Paster.
`main` is a name which will be used in an .ini file.
`myapp.startpoints:uwsgi` is dotted url for method which will return wsgi object.

After all that, you can create the egg.

```bash
python setup.py develop
```

## Configuring Paster

Last file to create is an app.ini. This file is an configuration for paster and
uwsgi (you can make 2 different files for that, but it is a good idea to make
only one file).


```ini
[app:main]
    use = egg:myapp

[server:main]
    use = egg:waitress#main
    host = 0.0.0.0
    port = 8000

[uwsgi]
    socket = 0.0.0.0:8000
    chdir = /code
    master = true
    need-app = true
    processes = 4
    pythonpath = *.egg

[pipeline:main]
    pipeline =
        main
```

`[app:main]` section is here to tell the paster which egg to use. Paster use
this egg to search for `paste.app_factory` section in entry_points. This is
how the uwsgi/Paster knows which startpoint to use and this is why the setup.py
is an important file.

This section is also used for Pyramid's settings, but the Sapp is not using it
at all, because we use Setting's plugins.

`[server:main]` sections is here to configure the development server. `waitress`
is a simple www server for development purpose. More info about waitress can be
found [here](https://docs.pylonsproject.org/projects/waitress/en/latest/)

`[uwsgi]` section will configure the uwsgi process. Description of all the
options can be found [here](http://uwsgi-docs.readthedocs.io/en/latest/Options.html)

Description for the `[pipeline:main]` section can be found [here](http://docs.repoze.org/moonshining/tools/paste.html#example-configuring-the-wsgi-pipeline)

More info about the Paster .ini file can be found here:

- [Launching the Application](https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/pylons/launch.html)
- [INI File](https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/pylons/ini_file.html)


## Starting development server

In order to start the development server you need to run pserve with a path for
`app.ini` file. It is usefull also to add `--reload` switch, so the server will
be restarted every time the python files will change.

```bash
pserve app.ini --reload
```

## Starting uwsgi server

In order to start uwsgi process, you need to use `--ini-paste` switch with a
path to an `app.ini` file.

```bash
uwsgi --ini-paste app.ini
```

## Creating Plugins for Pyramid

`ConfiguratorWithPyramid` will run `start_pyramid(pyramid)` method for all
plugins when running `.make_wsgi_object`. Of corse, if the configurator will not
find the `start_pyramid` method, it will not complain, because otherwise the old
plugins would be not compatible with the `ConfiguratorWithPyramid`. So if you
want to make a Pyramid's specifyc plugin, you should just add
`start_pyramid(pyramid)` method to your normal plugin.

`pyramid` in `start_pyramid(pyramid)` method is pyramid.config.Configurator
instance.

Implementation of the CsrfPlugin should be a good example.

```python
class CsrfPlugin(Plugin):
    """
    Add csrf mechanism to the pyramid app.
    """

    def __init__(self, policy_cls):
        self.policy_cls = policy_cls

    def start(self, configurator):
        self.settings = configurator.settings

    def start_pyramid(self, pyramid):
        pyramid.set_csrf_storage_policy(self.policy_cls())
        pyramid.set_default_csrf_options(
            require_csrf=True,
            token=self.settings['csrf_token_key'],
            header=self.settings['csrf_header_key'])
```

# Routing Wrapper

TODO

# Controllers

TODO

# BaseWebTestFixture

TODO
