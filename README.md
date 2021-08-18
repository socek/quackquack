# Quack Quack

If it quacks like a quack, then it's a Quack Quack.
Version: 1.0.0

# Table of Contents
1. [Overview](#overview)
2. [Quick Using Guide](#quick-using-guide)
3. [Installation](#installation)
4. [Tutorial](docs/tutorial.md)
    * [Configuration](docs/tutorial.md#configuration)
    * [Starting](docs/tutorial.md#starting)
    * [Using Context](docs/tutorial.md#using-context)
    * [Using Injectors](docs/tutorial.md#using-injectors)
    * [Creating Plugins](docs/tutorial.md#creating-plugins)
5. [Plugins](docs/plugins.md)
    * [Settings](docs/plugins.md#settings)
    * [Logging](docs/plugins.md#logging)
    * [Redis](docs/plugins.md#redis)
    * [Pyramid Plugin](docs/pyramid.md)
    * [Sqlalchemy Plugin](docs/sqlalchemy.md)
    * [Json Plugin](docs/json.md)
6. [Phases](docs/phases.md)
    * [About Phases](docs/phases.md#about-phases)
    * [Phase 0](docs/phases.md#phase-0)
    * [Phase 1 - creating Configurator instance](docs/phases.md#phase-1---creating-configurator-instance)
    * [Phase 2 - starting Configurator](docs/phases.md#phase-2---starting-configurator)
    * [Extending Phases](#extending-phases)
    * [Application Phase Start](docs/phases.md#application-phase-start)
    * [Application Phase End](docs/phases.md#application-phase-end)
7. More info
    * [Changelog](docs/CHANGELOG.md)
8. [Example](example/readme.md)


# Overview

This project aims to resolve problem of configuring an application, which needs to
have initialization step (for example: for gathering settings or establishing
connections) and use Python style code (context managers and decorators) to get
those data.

For example, normally you would need to use two separate mechanism for settings
in celery application and web application, because you should not use web
application startup process in the celery app. This package provide a solution
for this problem, by giving one simple and independent of other frameworks
mechanism to implement everywhere.

# Quick Using Guide

To use Quack Quack you need to create the application class (inherited from
`qq.Application`) in which you need to add plugins. After configuring, you need to "start"
the application. After that you can use the configurator as context manager.

```python
from qq import Application, Context
from qq.plugins import SettingsPlugin

class MyApplication(Application):
    def create_plugins(self):
        self.plugins["settings"] = SettingsPlugin('esett')

application = MyApplication()
application.start('application')

with Context(application) as ctx:
    print(ctx["settings"])

```

`context.settings` in above example is variable made by the SettingsPlugin.
If you would like to know more, please go to the [Tutorial](docs/tutorial.md)

# Installation

```bash
pip install quackquack
```
