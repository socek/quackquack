# Simple Application

Version: 0.4.0

# Table of Contents
1. [Overview](#overview)
2. [Quick Using Guide](#quick-using-guide)
3. [Installation](#installation)
4. [Tutorial](docs/tutorial.md)
    * [Configuration](docs/tutorial.md#configuration)
    * [Starting](docs/tutorial.md#starting)
    * [Using Context](docs/tutorial.md#using-context)
    * [Creating Plugins](docs/tutorial.md#creating-plugins)
    * [Extending Configurator](docs/tutorial.md#extending-configurator)
5. [Plugins](docs/plugins.md)
    * [Settings](docs/plugins.md#settings)
    * [Logging](docs/plugins.md#logging)
    * [JSON](docs/plugins.md#json)
    * [Redis](docs/plugins.md#redis)
    * [Pyramid Plugin](docs/pyramid.md)
    * [Sqlalchemy Plugin](docs/sqlalchemy.md)
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

This project will help starting an application, which needs to have initialization
step at the beginning (for example: for gathering settings) and use them in many
places/endpoints.
For example, normally you would need to use two separate mechanism for settings
in celery application and web application, because you should not use web
application startup process in the celery app. This package provide solution
for this problem, by providing one simple and independent (for use in any place)
mechanism to use everywhere.

# Quick Using Guide

To use Simple Application (Sapp for short) you need to inherit from Configurator
in which you need to add some plugins. After configuring, you need to "start"
the application. After that you can use the configurator as context manager.

```python
from sapp import Configurator, ContextManager
from sapp.plugins import SettingsPlugin

class MyConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin('path.to.settings'))

application = MyConfigurator()
application.start('application')

with ContextManager(application) as ctx:
    print(ctx.settings)

```

`context.settings` in above example is variable made by the SettingsPlugin.
If you would like to know more, please go to the [Tutorial](docs/tutorial.md)

# Installation

```bash
pip install sapp
```
