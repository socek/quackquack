SQLAlchemy Plugin
=================

About
-----

SQLAlchemy plugin is just a wrapper for SQLAlchemy. This plugin allows starting
database session at context phase start and closing it at context phase end.

Dependencies
------------

* SettingsPlugin
* SqlAlchemy
* Alembic

Example implementation
----------------------

.. code-block:: python

   from qq import Application
   from qq.plugins.settings import SettingsPlugin
   from qq.plugins.sqlalchemy.plugin import SqlAlchemyPlugin

   class MyApplication(Application):
       def create_plugins(self):
           self.plugins(SettingsPlugin("myapp.application.settings"))
           self.plugins["database"] = SqlAlchemyPlugin()


Before you cane use this code, you need to make proper settings. Example:

.. code-block:: python

   def default() -> Settings:
       settings = Settings()
       settings["database"] = database()
       return settings

   def database() -> Settings:
       name = os.get_env("DB_NAME")
       user = os.get_env("DB_USER")
       password = os.get_env("DB_PASSWORD")
       host = os.get_env("DB_HOST")
       return {
           "url": f"postgresql://{user}:{password}@{host}:5432/{name}",
           "options": {
               "pool_recycle": os.get_env("DB_POOL_RECYCLE", 3600, cast=int),
               "pool_pre_ping": os.get_env("DB_PRE_PING", True, cast=bool),
               "pool_size": os.get_env("DB_SIZE", 40, cast=int),
               "max_overflow": os.get_env("DB_OVERFLOW", 20, cast=int),
           },
       }


Settings description
--------------------


* url - sqlalchemy url for the database
* options - dict of options which will be passed to a ``sqlalchemy.engine.create_engine``.
  For more info visit `SQLAlchemy docs <http://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine>`_

Defining sql table
------------------

All tables can be defined using SqlAchemy's ORM. Code below is a simple
definition of such base table.

Also it implements TableFinder which is used for searching all defined tables
in our package. This will be used in the Alembic integration later.

.. code-block:: python

   from datetime import datetime
   from uuid import uuid4

   from qq.finder import ObjectFinder
   from sqlalchemy import Column
   from sqlalchemy import DateTime
   from sqlalchemy import Integer
   from sqlalchemy.dialects.postgresql import UUID
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.schema import MetaData

   # Recommended naming convention used by Alembic, as various different database
   # providers will autogenerate vastly different names making migrations more
   # difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
   NAMING_CONVENTION = {
       "ix": "ix_%(column_0_label)s",
       "uq": "uq_%(table_name)s_%(column_0_name)s",
       "ck": "ck_%(table_name)s_%(constraint_name)s",
       "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
       "pk": "pk_%(table_name)s",
   }
   metadata = MetaData(naming_convention=NAMING_CONVENTION)


   class Base:
       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

       def _asdict(self):
           data = dict(self.__dict__)
           del data["_sa_instance_state"]
           return data


   class TableFinder(ObjectFinder):
       def is_collectable(self, element: object):
           try:
               return issubclass(element, SqlTable) and element != SqlTable
           except TypeError:
               return False


   SqlTable = declarative_base(cls=Base, metadata=metadata)


Using in the context
--------------------

In order to use the database in the context, just get the main key from the
context like this (assuming your main key is "database"):

.. code-block:: python


   with app as context:
     context["database"].query(User).all()


Inicjators
----------

There was no point in creating additional injectors, so you need to create your
own, for example:

.. code-block:: python

    from qq.plugins.sqlalchemy.injectors import SesssionInicjator

    Query = SesssionInicjator("database")


And use it like this:


.. code-block:: python

    from sqlalchemy.orm.session import Session

    @SetInjector("psql", Query)
    def get_items(psql: Session):
        ...


Transactions and commiting
--------------------------

Normally, the commit should be done manually. But you can use TransactionInicjator
in order to have this done automaticly.

.. code-block:: python

    from qq.plugins.sqlalchemy.injectors import TransactionInicjator

    @SetInjector("psql", TransactionInicjator())
    def clear_reports(
        from_date: date,
        to_date: date,
        psql: Session,
    ) -> int:
        stmt = delete(SomeTable).where(
            BillingReportsTable.day >= from_date, BillingReportsTable.day < to_date
        )
        return psql.execute(stmt).rowcount


Integrate with Alembic
----------------------

Alembic is a library to manage migrations. Alembic makes a folder for the version
changes. This folder contains "env.py" file, which we need to change like this:

.. code-block:: python

   from qq.plugins.sqlalchemy.alembic import run_migrations

   from PACKAGE import application
   from PACKAGE.app.db import SqlTable
   from PACKAGE.app.db import TableFinder

   application.start("default")
   TableFinder([DOTTED_PATH_TO_PACKAGES], [DOTTED_PATH_TO_MODULES_TO_IGNORE]).find()
   run_migrations(application.globals["dbsession"], SqlTable.metadata)


First, you need to import the app object and base Model if you use SQLAlchemy
ORM. Also, you need to import all the models in this file, if you want to use
"--autogenerate". Last, but not least you need to run AlembicScript.

For more info, you can go to the Alembic `documentation <http://alembic.zzzcomputing.com/en/latest/>`_
