# Qapla - About

This project is pyramid's boilerplate code for applications. It is useful when you have couple of application using
pyramid and want to have the same code structure and similar configuration.
"Qapla'" is a Klingon's world for "success".

# Features

1. Controller as a class instead of methods with a simple flow and configuration from class properties
2. 4 controller types:
 * Controller (return templates)
 * JsonController (return json)
 * RestfulController (designed for restfull apps)
 * FormController (designed for form validation in restfull apps)
3. Boilerplate for
 * Integration with morfdict (settings)
 * Integration with Sqlalchemy and Alembic
 * Testing fixtures for py.test

# Installation

```
pip install qapla
```

You should add "qapla==0.1" into you requiretment's list (either if you have requiretments.txt or in setup.py). Please
be aware that qapla versions will not be backward compatible, so you need to use fixed version instead of something like
"qapla>=0.1". Qapla have no fixed version for it's requiretment so please also be aware that after upgrading for example
pyramid, the qapla can stop working. So you should fix the pyramid's version in your application.

# How to use

Qapla is designed to use it's features separately.

## Application boilerplate + settings integration

Example Application class is looking like this:

```python
from qapla.app import Application
class RotarranApplication(Application):

    class Config(Application.Config):
        settings_module = 'rotarran.application'

    def append_plugins(self):
        self.add_routing(RotarranRouting)
        self.add_auth(
            AuthTktAuthenticationPolicy,
            ACLAuthorizationPolicy,
            RotarranFactory)
        self.add_sessions(SignedCookieSessionFactory)
        self.add_csrf_policy(SessionCSRFStoragePolicy)

main = RotarranApplication()
```

First we need to create Application class. Application.Config.settings_module is python url for where the settings
will be stored (morfdict support configuration in many files, for example "default.py" + "local.py"). After that we
should add some plugins. In this example we add plugins for:
- routing - which comes with routing as .yml file
- auth
- session
- csrf

All these plugins can be configured in normal pyramid way.
The "main" variable is for pyramid's configuration. This is the object which needs to be configured when creating egg
for the pyramid's application, example:

```python
setup(
    name='rotarran',
    packages=find_packages(),
    entry_points={
        'paste.app_factory': [
            'main = rotarran:main'
        ],
    }
)
```

### Sqlalchemy and alembic integration

In order to make our application able to use database thru sqlalchemy and migration thru alembic, first we need to make
our Application class inherit from DatabaseApplication. After that we need to add .add_database method into append_plugins
section.

```python
from qapla.database import DatabaseApplication

class RotarranApplication(DatabaseApplication):

    def append_plugins(self):
        self.add_database()
```

Unfortunetly you need to make proper alembic configuration on your own.

## Controller

### flow

Qapla's controller is very simple.

```python
from qapla.controller import Controller

class HomeController(Controller):

    renderer = 'path/to/template.jinja2'

    def make(self):
        self.context['yey'] = 'it worked!'
```

This sample controller will render html from template using context. There is no
more magic behind this. Configuration by class properties works only if you use
qapla.routing.Routing for your routing configuration.

Flow of running the controller
1. _create_context() - create default context
2. _before_make() - do some stuff before make
3. _make() - run .make method
4. _after_make() - do some stuff after make
5. _create_widgets() - add something into the context
6. _get_response() - return prepered response or create new one if not created

Before and after make methods are places to make something like "context processor"
in django (code which will be runned around normal controller code). In order
to proper use of these you need to inherite from controllers with these method
overwritten.

_make method is a wrapper for .make which, besides running .make, will catch
FinalizeController error. This is an error which will end the .make method, but
run the rest of the controller flow. Another useful error is QuitController,
which will end the request without finishing the controller flow. FinalizeController
will run ._after_make and ._create_widgets method, but QuitController will not.

If you will not create response object, the default one will be used. If you would
like to create response, you need to set Controller.response property, for example:

```python
self.response = HTTPFound(
    location=url,
    headers=self.request.response.headerlist,
)
```

_create_widgets method will be called only, if you have no response created in the
.make mthod.

### Controller helpers

.redirect method will make HTTP 302 redirection response. If you use quit=True,
then this method will raise QuitController.

### JsonController

This controller will return json (generated from .context) instead of rendered
template.

### RestfulController

This controller will return json and have proper HTTP REST method to use within
the controller:

1. def get(self):
2. def post(self):
3. def put(self):
4. def patch(self):
5. def delete(self):

## Drivers

Drivers methodology is implemention of "Command Query Responsibility Segregation".
It seperates using the database in controllers. In between we will use 2
drivers: write and read. Sometimes they will return the objects and sometimes
the raw data in dict/list. Using this methodology we can separate unit tests
(mocking drivers) with integration one (testing drivers).

In order to use drivers, you should make 2 classes:

```python
class ModelReadDriver(ReadDriver):
    model = Model


class ModelWriteDriver(WriteDriver):
    model = Model
```

In the controller you should use:

```python
read_driver = ModelReadDriver(self.request.database)

obj = read_driver.get_by_id(1)
```

Or something like that. All code which involves saving/reading from database
should be whitn method inside Read or Write driver.