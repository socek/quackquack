# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning]
(http://semver.org/).

## 0.5.0 - (TODO)

- Switch from pipfile into poetry and from setup.py into pyproject.toml
- Decorator should not start an context if it's not needed.
- Change settings of DatabasePlugin from a form of "db:dbname:url" into normal dict: {"databases": {"dbname": {"url": "x"}}}
- Add recreate for DatabasePlugin and remove old recreate mechanism, including using "default url".
- Removed old "driver" support for DatabasePlugin. Preparing code for CQRS instead, like "command" and "query" wrappers.

## 0.4.0 - Split Context Manager and Decorator for Configurator

### Added

- ContextManger class, so the configurator will act as context manager
- Decorator class, so the configurator will act as decorator
- Example for application that uses pyramid, celery, tornado, gevent at the same time

### Removed

- Functionality that allowed to use Configurator as decorator and context manager simultaneously

## 0.3.0 - Plugins and documentation

### Added

- JSON plugin (makes uuid4 serializable)
- REDIS plugin
- Add documentation for Fragment Context.

## 0.2.0 - Fragment Context

### Added

- Fragment Context mechanism

## 0.1.0 - First Release

### Added

- Confiugator
- Context
- Settings Plugin
- Logging Plugin
- Pyramid Plugin
- SQLalchemy Plugin
