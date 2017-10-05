# Qapla - Database

# Table of Contents
1. [About](#about)
    1. [Main problems](#main-problems)
    2. [Test environment](#test-environment)
    3. [More info](#more-info)
2. [Configuration](#configuration)
    1. [Application](#application)
    2. [Migration - Alembic](#migration---alembic)
3. [How To Use](#how-to-use)
    1. [Web server - request](#web-server---request)
    2. [Migration](#migration)
    3. [Celery](#celery)
    4. [Tests](#tests)
    5. [CQRS](#cqrs)

## About

Managment of the database is a pretty complicated job. That is why we had to make a wrapper for the problem. We need to
cover these problems:

* multi database
* database session for request
* database session for celery task
* migrations with auto generate function
* database session for tests with recreation (drop database and create new one at the tests start)

### Main problems

The main problem is that, we need to gather the settings and start an application with some features (for example: start logging or connect to the database). Let's call this phase "app preparation". We should use the database session only after the app preparation is finished.
Second problem is that we work on the multi threaded environment and doing so, we need to be aware of when the database session is started and closed or otherwise we will get some strange sqlalchemy's errors.

Before we can implement anything, we need to think of a way to be able to connect to a many databases or else we will end up like Django 5 years from now.

The first problem with request is very simple. We can just use the request lifetime for the session and that will work perfectly for us, because 1 request will live in 1 process.
For the celery tasks we would need to pass the session object to the task, which will then pass it on when needed. I thinking about a decorator which will get the application object and add the database session to the task's args.
For migration we are using alembic, so we need to plug in to it. Every migrations directory has an `env.py` file, which we can use and prepare the app before migration. This will give us one place to store url (and options) for the database. I think the best way of managing many databases in here is to use separate migrations directory for every database and we will just set the name of the database in the `env.py`.
For the auto generation we need to have all involved models imported somewhere, so the alembic can detect them. I think the best place for this is in the `env.py` file.

SqlAlchemy has a way to help programmers implementing session mechanism in the multi threaded environment. This is the scoped_session described in the link below (Must Read section).


### Test environment

When starting the tests, the problem gets a little bit bigger. First of all, we need to have a way for switching between the test database and the main one. This is achieved thanks to the `morfdict` module which we use. Now we have `settings/default.py` file which is used always. When we use Application.run_tests for preparing the application the the `settings/tests.py` file will be overwrite the `default.py` configuration. So now we will have configuration to the test database. In the env.py we need to find a way to be able to tell if this is a test environment or not.
Next problem is recreating the database (drop, create and migrate). In the postgres there is a fail safe which forbids dropping of a database which has any connection (even the one we use to drop). That is why we need to connect to a different database (for example "postgres" database) and drop the test database from there. After that we can run alembic migrations.


### More info

http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-faq-whentocreate
http://docs.sqlalchemy.org/en/latest/orm/contextual.html#contextual-thread-local-sessions

## Configuration

### Application

In order to make our application able to use database thru sqlalchemy and migration thru alembic, first we need to make
our Application class inherit from DatabaseApplication. After that we need to add .add_database_app method into
append_app_plugins and add_database_web into append_web_plugins section. `add_database_app` method needs list of the
databases to configure (we can use more than one). The name 'main' is very important, because it will be used in many
places.


```python
from qapla.database.application import DatabaseApplication
from qapla.database.database import Database

class RotarranApplication(DatabaseApplication):

    def append_app_plugins(self):
        self.add_database_app([Database('main', 'migrations')])

    def append_web_plugins(self):
        self.add_database_web()
```

Database integration is a plugin that do not need pyramid, that is why it needs to be plugged in on the app plugins step.
The second argument for the Database is key for paths for the migrations directory. For example: `/code/migrations`

### Migration - Alembic

For using alembic you need to first create alembic.ini file and put there something like this:

```
[alembic]
script_location = /code/migrations
```

Where `/code/migrations` is a path to the migrations directory. You should also configure the migrations directory in the
paths settings. Now you need to initialize the alembic directory:

```
$ alembic init /code/migrations
```

This wil create directory and a file /code/migrations/env.py which we need to edit, so it will look like this:

```python
from qapla.database.env import AlembicEnv

from rotarran import main
from rotarran.application.db import Model

AlembicEnv(main, Model, 'main').run()
```

Where `rotarran` module is our package with application. `rotarran.main` is a `qapla.database.DatabaseApplication`
instance and `rotarran.application.db.Model` is Sqlalchemy Base Model.

`AlembicEnv` is a class which will help us with managing migrations from many places.

## How To Use

### Web server - request

For using the database session, you can get the database session from the request object. Just get the name provieded
in the configuration, like it was a normal property. Example:

```python
request.main.query().all()
```

The session will be closed after the request is finished, but you need to commit by yourself.

### Migration

For migration you should use normal alembic command line. How to use alembic you can see
[here](http://alembic.zzzcomputing.com/en/latest/)

### Celery

For use in the celery, we need to explicitly use the database from the Application instance. We would need to make sure,
that this session is closed. That is why you can use `qapla.database.decorators.WithDatabase` as a decorator on the task.
So now, after the tasks ends, the session will be closed.

```python
from qapla.database.decorators import WithDatabase
from rotarran import main

@WithDatabase(main, 'main')
def mytask(main):
    #main object will be sqlalchemy session
```

### Tests

Unit Tests should not prepare the application or connect to the database, but the integration tests should do that.
That is why we have created `qapla.database.testing.BaseApplicationFixture` which use pytest's fixtures to prepere the
app and create database session. Example should be self explanatory:

```python
from qapla.testing import BaseApplicationFixture

from rotarran.application.app import RotarranApplication


class ApplicationFixture(BaseApplicationFixture):
    APP_CLASS = RotarranApplication
    DATABASE_KEY = 'main'

class TestSomething(ApplicationFixture):

    def test_session(self, dbsession):
        # dbsession is sqlalchemy database session
```

Avalible fixtures:
- application - this is the preperated application object, which uses `.run_tests` for the preperation. It imples that
    the application use the tests configs.
- dbplugin - the datbase plugin with all the databases configured
- dbsession - db session configured by the DATABASE_KEY property.

### CQRS

You can use the [CQRS](https://martinfowler.com/bliki/CQRS.html) methodology. For this we have designed ReadDriver and
WriteDriver in the `qapla.driver` module. Using it is very simple. You should have ReadDriver and WriteDriver for every
model you use.

It seperates using the database in controllers. In between we will use 2 drivers: write and read. Sometimes they will
return the objects and sometimes the raw data in dict/list. Using this methodology we can separate unit tests (mocking
drivers) with integration one (testing drivers).

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

Or go to class and check available methods. All code which involves
saving/reading from database should be whitn method inside Read or Write driver.
