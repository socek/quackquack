*********
Changelog
*********

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/>`_ and this project adheres to [Semantic Versioning]
(http://semver.org/).

Version: 1.3.2
==============

* Add
    * async support for sqlalchemy


Version: 1.3.1
==============

* Add
    * async functions and injectors support


Version: 1.3.0
==============

* Add
    * Injectors - new way of dependency injection (with @SetApplication and @SetInjector)
* Removed
    * Removed ApplicationInitializer


Version: 1.2.1
==============

* Update dependecy packages

Version: 1.2.0
==============

* Add
    * Injectors - new way of dependency injection
    * async functions support
* Renamed
    * Rename InjectApplication into ApplicationInitializer.
* Removed
    * Remove SAQuery (in favour of SessionInjector) and SACommand (in favour of TransactionDecorator).
    * Drop pyramid support.
    * Remove jsonhack
    * Remove DataclassFinder.

Version: 1.1.1
==============

* Fixed
    * Added Pickling of the Application object, so FastAPI will no longer crash when tried to log a request.

Version: 1.1.0
==============

* Added
    * Support for inject application into coroutine.

Version: 1.0.5
==============

* Added
    * Add Plugin validation.
    * Add Singleton Plugins functionality.
    * Add Plugin Container in Application.
* Changed
    * Use Plugin Container instead of OrderedDict for plugins.
* Fixed
    * Overwriting the `self` when using `InjectApplication` decorator
    * Better error info when Injector not inicialized

Version: 1.0.4
==============

* Added
    * Injectors can have injectors in arguments. Application object will be forwarded from to the top to the bottom.
    * @InjectApplication (or @InitializeInjectors before) functions now can have another @InjectApplication functions in default arguments. Application object will be forwarded from to the top to the bottom.
* Changed
    * Renamed InitializeInjectors into InjectApplication
    * Documentation from Markdown into reStructuredText
* Fixed
    * Starting and running of injectors.

Version: 1.0.3
==============

* Fixed
    * Add missing const for settings plugin.

Version: 1.0.2
==============

* Fixed
    * Release fix: the release configuration was broken, but the code did not changed (yes, second time :/).

Version: 1.0.1
==============

* Fixed
    * Release fix: the release configuration was broken, but the code did not changed.

Version: 1.0.0
==============

* Changed name from sapp to Quack Quack
* Change behavoiur of the application and contexts: removex ContextManager and LazyContextManager in favor of always lazy Context.
* Remove decorator injecting dependencies in favor of injectors

Version: 0.5.0
==============

* Switch from pipfile into poetry and from setup.py into pyproject.toml
* Decorator should not start an context if it's not needed.
* Change settings of DatabasePlugin from a form of "db:dbname:url" into normal dict: {"databases": {"dbname": {"url": "x"}}}
* Add recreate for DatabasePlugin and remove old recreate mechanism, including using "default url".
* Removed old "driver" support for DatabasePlugin. Preparing code for CQRS instead, like "command" and "query" wrappers.
* Fixed problem with starting context again
* Cleaned up dependecies
* Changed and improved alembic migration scripts. Now it allows to start the app by the developer instead of the code.
* Added Object Finder.
* Added JsonHack.
* New encoder: Decimal and new way of adding encoders (sapp.plugins.jsonhack.models.add_encoder).
* Change View class so all of the ednpoint will get the request as a param.


Version: 0.4.0 - Split Context Manager and Decorator for Configurator
=====================================================================

* Added
    * ContextManger class, so the configurator will act as context manager
    * Decorator class, so the configurator will act as decorator
    * Example for application that uses pyramid, celery, tornado, gevent at the same time
* Removed
    * Functionality that allowed to use Configurator as decorator and context manager simultaneously

Version: 0.3.0 - Plugins and documentation
==========================================

* Added
    * JSON plugin (makes uuid4 serializable)
    * REDIS plugin
    * Add documentation for Fragment Context.

Version: 0.2.0 - Fragment Context
=================================

* Added
    * Fragment Context mechanism

Version: 0.1.0 - First Release
==============================

* Added
    * Confiugator
    * Context
    * Settings Plugin
    * Logging Plugin
    * Pyramid Plugin
    * SQLalchemy Plugin
