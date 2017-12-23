from sqlalchemy.engine.url import make_url

from sapp.plugins.sqlalchemy.exceptions import SettingMissing


class DatabaseSetting(object):
    """
    Settings for the database.
    This class will help set settings for the database. Making settings key may
    be a little bit difficult, that is why this class is design for.

    Expected values:
    - url* - url for the sqlalchemy database
    - default_url* - url for different sqlalchemy database which allows dropping
        and creating the first one
    - options - arguments which will be passed to the sqlalchemy's create_engine

    * - mandatory arguments, which wll be validated and raise an error if don't.
    """
    _PREFIX = 'db'
    _TO_VALIDATE = ('url', 'default_url')

    def __init__(self, settings, name='database'):
        self.name = name
        self.settings = settings

    def get_key(self, subkey=None):
        keys = [self._PREFIX, self.name]
        if subkey:
            keys.append(subkey)
        return ':'.join(keys)

    def __getitem__(self, subkey):
        key = self.get_key(subkey)
        return self.settings[key]

    def __setitem__(self, subkey, value):
        key = self.get_key(subkey)
        self.settings[key] = value

    def get(self, subkey, default=None):
        key = self.get_key(subkey)
        return self.settings.get(key, default)

    def validate(self):
        for subkey in self._TO_VALIDATE:
            self.validate_exists(subkey)
            make_url(self[subkey])

    def validate_exists(self, subkey):
        key = self.get_key(subkey)
        if key not in self.settings:
            raise SettingMissing(key, self.name)
