# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning]
(http://semver.org/).

## 0.4.0 - 2017-10-10
### Changed
- Way of configuring database. Old: sperate for host, port, database and so on. New: Every database should have database
    setting on its own.
- Application.Config changed name to a Application.MetaConfig

### Added
- Add WidthDatabase decorator.

### Fixed
- Starting of the database in the tests envoritment


## 0.3.1 - 2017-09-15
### Fixed
- Database fixture for testing

## 0.3.0 - 2017-09-14
### Added
- 2 step plugins

## 0.2.1 - 2017-09-04
### Fixed
- Migration for tests script

## 0.2.0 - 2017-09-04
### Added
- Logging support.
- Add routing documentation

## 0.1.0 - 2017-08-31
### Added
- Application's configuration
- Database plugin with sqlalchemy and alembic
