# SQLAlchemy Plugin

0. [Go Home](../README.md)
1. [About](#about)
2. [Installation](#installation)
3. [Using in context](#using-in-context)
4. [Integrate with Alembic](#integrate-with-alembic)
5. [CQRS like drivers](#cqrs-like-drivers)

# About

SQLAlchemy plugin is just a wrapper for SQLAlchemy. This plugin allows starting
database session at context phase start and closing it at context phase end.

# Installation

In order to use the plugin, you need to add the plugin to the Configurator.
Database plugins needs the SettingsPlugin as well.

```python
from sapp.configurator import Configurator
from sapp.plugins.settings import SettingsPlugin
from sapp.plugins.sqlalchemy.plugin import DatabasePlugin

class MyConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin('myapp.application.settings'))
        self.add_plugin(DatabasePlugin('dbsession'))
```

Argument for the DatabasePlugin is the name for the session which will be used
in many places, like context or settings. Let's call it "main key".

Before you cane use this code, you need to make proper settings. Example
settings:

```python
def database(settings):
    settings['db:dbsession:url'] = 'postgresql://name:password@postgres:5432/dbname'
    settings['db:dbsession:default_url'] = 'postgresql://name:password@postgres:5432/postgres'
    settings['db:dbsession:options'] = {
        'pool_recycle': 3600
    }
```

As you can see here, to proper settings key name is "db:" prefix with main key.
The last part is one of the values name:

- url - sqlalchemy url for the database
- default_url - sqlalchemy url for the default database. This settings is needed
  when you wanto to recreate the database. PostgreSQL do not allow to drop
  database which you are connected to. That is why we need to connect to a second
  database. `postgres` is a good second database, because this database is always
  existing on the postgresql servers.
- options - dict of options which will be passed to a `sqlalchemy.engine.create_engine`.
  For more info visit [SQLAlchemy docs](http://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine)

# Using in context

In order to use the database in the context, just get the main key from the
context like this (assuming your main key is "dbsession"):

```python

with app as context:
  context.dbsession.query(User).all()
```

# Integrate with Alembic

Alembic is a library to manage migrations. Alembic makes a folder for the version
changes. This folder contains "env.py" file, which we need to change like this:

```python
# flake8: noqa
from sapp.plugins.sqlalchemy.alembic import AlembicScript

from myapp import app
from myapp.application.model import Model

# import or define all models here to ensure they are attached to the
# Model.metadata prior to any initialization routines

import myapp.answers.models


AlembicScript(app, Model, 'dbsession').run()
```

First, you need to import the app object and base Model if you use SQLAlchemy
ORM. Also, you need to import all the models in this file, if you want to use
"--autogenerate". Last, but not least you need to run AlembicScript.

For more info, you can go to the Alembic [documentation](http://alembic.zzzcomputing.com/en/latest/)

# CQRS like drivers

You can also use [CQRS](https://martinfowler.com/bliki/CQRS.html) like objects.
For this puprose, you can use `sapp.plugins.sqlalchemy.driver.Query` and
`sapp.plugins.sqlalchemy.driver.Command` classes.

```python
from sapp.plugins.sqlalchemy.driver import Query
from sapp.plugins.sqlalchemy.driver import Command

from myapp.auth.models import User


class UserQuery(Query):
    model = User

    def _get_by_email(self, email):
        return self.query().filter(self.model.email == email)

    def find_by_email(self, email):
        return self._get_by_email(email).first()


class UserCommand(Command):
    model = User

    def create(self, **kwargs):
        password = None
        obj = self.model()
        password = kwargs.pop('password', None)

        for key, value in kwargs.items():
            setattr(obj, key, value)

        if password:
            obj.set_password(password)

        self.database.add(obj)
        self.database.commit()

        return obj
```

`Query` class is for reading the database. The convetion here is simple:

- methods with "_" prefix should return QuerySet
- methods with normal name should return objects or data
  - methods with "get_" prefix should get one object or raise an error
  - methods with "first_" prefix should get one object or return `None`
  - methods with "list_" prefix should return iterable or list

`Command` class is for writing to the database. The convention here is a different:

- method with "_" prefix should not commit to the database.
- method with normal name should commit to the database.

Pre-implemented methods are:

- `Query`
  - `._query()` - query the model
  - `.get_by_id(id)` - get user by the id
  - `.list_all()` - list all of the objects from the database
- `Command`
  - `.create(**kwargs)` - create instance of the model in the database
