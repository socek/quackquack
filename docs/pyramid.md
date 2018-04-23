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
    * [Why we need a router wrapper](#why-we-need-a-router-wrapper)
    * [How to implement Routing](#how-to-implement-routing)
4. [Views](#views)
    * [Base View](#base-view)
    * [JsonView](#jsonview)
    * [HttpMixin: HttpView and RestfulView](#httpmixin-httpview-and-restfulview)
5. [BaseWebTestFixture](#basewebtestfixture)

# About

Pyramid Plugin is a set of couple of features:

- [Extended Configurator](#extended-configurator) and plugins - allows to creat
    wsgi object for uwsgi
- [Routing Wrapper](#routing-wrapper) - allows to get view value from class
    variables
- [Views](#views) - view classes with support of http methods
- [BaseWebTestFixture](#basewebtestfixture) - fixtures for pytest to use webtest

All these features can be used separately.

# Extended Configurator

Pyramid Framework gives you possibility to create wsgi application, which can be
used by the uwsgi/gunicorn/etc. process. Pyramid is using Paster to configure
the wsgi application, this means you need to configure some stuff in the
Paster/Pyramid way.

## Implement Configurator

Implementing the Configurator is pretty simple. The only thing needed to be done
is to inherited your Configurator from `ConfiguratorWithPyramid` insted of the
normal configurator. The new Configurator will be responsible for running
Pyramid's plugins as well.

For example, we will add SettingsPlugin fro Sapp and RoutingPlugin from Sapp's
Pyramid Plugin.

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
ones. More about plugins can be found [here](#creating-plugins)

## Implement Startpoint

Second step of implementing Pyramid's Plugin is to create a startpoint. It needs
to be a function which will return an wsgi object, which will be used by uwsgi
and paster. In order to do that we need to start the Configurator.

Example:

```python
from myapp import app


def wsgi(settings): # settings is dict with configuration from .ini file
    app.start('pyramid')
    return app.make_wsgi_object()
```

The settings argument is not used here. It is something that will be passed to
the function by the uwsgi or paster, but Sapp Settings does not use it at all.

## Configuring Egg

You need to have proper setup.py which will create an egg for us (otherwise the
Paster will not work). Creating of proper setup.py is described in the Python's
Documentation [here](https://docs.python.org/3.6/distutils/setupscript.html).

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
at all, because we use Setting's plugin.

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
be restarting every time the python files will change.

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

## Why we need a router wrapper
`sapp.plugins.pyramid.routing.Routing` was designed to simplify creating of
routes. In normal Pyramid, the developer needs to configure the route in one
place and the view in another. Also, configuring is made by @view_config
decorators which is not a good way if you want to share some values between
many classes, you can not use polymorphism. Instead you uneed to copy these
configuration variables across all the views.

Another disadvantage of normal pyramid's routing is that the linking of the
route and the view is made by name which is not very sophisticated and it
is very buggable.

## How to implement Routing

First step is to implement Routing class inherited from
`sapp.plugins.pyramid.routing.Routing` and make a `make(self)` method.
This is our wrapper for normal pyramid routing. It will help us, but if you want
to use the old ways, you are free to do that. `pyramid` property from the
`Routing` class is a [Pyramid Configurator](https://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator).

The `make(self)` should add all the routes, but you can import routes from
another module. Using import system makes this very simple and easy to read, but
please be aware, that you should not import `Sapp Configurator` instance, because
it will raise cross import error. Also you should not import the views,
because it may raise the same error as well. You should use only dotted strings.

Example:


```python
from sapp.plugins.pyramid.routing import Routing

from myapp.home.routing import home_routing

def not_home_routing(routing):
    routing.add('mypet.not_home.views.NotHome', 'not_home', '/not')

class MyappRouting(Routing):
    def make(self):
        home_routing(self)
        not_home_routing(self)
```

Only method which is needed description here is `Routing.add`. First argument is
dotted path to the view (or view class if you wish). Second is route
name. Third is the route url. All other args and kwargs will be passed to the
[add_route](https://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator.add_route) method. In order this route
to work, the Routing wrapper will call the [add_view](https://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator.add_view)
method. All the kwargs for this method will be taken from the view class.

Example view:

```python
class View(object:
    rendered = 'json'

    def __init__(self, root_factory, request):
        self.root_factory = root_factory
        self.request = request

    def __call__(self):
        return {}
```

# Views

Sapp comes with base class for every View.

Main reason to implement an view is to generate response proper response.
The simples way to return the data is to implement `.get(self)` method and
return a dict.

```python
from sapp.plugins.pyramid.view import View


class Home(View):
    renderer = 'json'

    def get(self):
        return {'hello': 'world'}
```

The renderer property here is to configure the view, so the framework will know
that this view will return json data. More info about the configuration
properties can be found [here]((#how-to-implement-routing)).

If you want to create a view which return template, you can implement it in this
way:

```python
from sapp.plugins.pyramid.view import View


class Home(View):
    renderer = 'templates/hello.jinja2'

    def get(self):
        return {'hello': 'world'}
```

Name o the methods is almost the same as the HTTP methods:

- .get

    Requests using GET should only retrieve data and should have no other effect.

- .post

    The POST method requests that the server accept the entity enclosed in the request as a new subordinate of the web resource identified by the URI.

- .put

    The PUT method requests that the enclosed entity be stored under the supplied URI.

- .patch

    The PATCH method applies partial modifications to a resource.

- .delete

    The DELETE method deletes the specified resource.

- .options

    The OPTIONS method returns the HTTP methods that the server supports for the specified URL.

More info about HTTP methods can be found [here](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods)

## RestfulView

RestfulView is a View, which returns JSON.

# BaseWebTestFixture

TODO
