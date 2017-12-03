# Simple Application

# Table of Contents
1. [Overview](#overview)
2. [Quick Using Guide](#quick_using_guide)
4. More info
    1. [Changelog](docs/CHANGELOG.md)


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

To use Simple Application (Sapp for short) you need to inherit from Configurator,
add some plugins and use it as context manager.

```python
from sapp.configurator import Configurator
from sapp.plugins.settings import SettingsPlugin

class MyConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(SettingsPlugin('path.to.settings'))

main = MyConfigurator()

with main as app:
    print(app.settings)

```

`app.settings` in above example is variable made by the SettingsPlugin.

