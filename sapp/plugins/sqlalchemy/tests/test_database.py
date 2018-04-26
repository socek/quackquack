from pytest import fixture
from pytest import raises

from sapp.plugins.sqlalchemy.database import DatabaseSetting
from sapp.plugins.sqlalchemy.exceptions import SettingMissing


class TestDatabaseSetting(object):
    @fixture
    def settings(self):
        return {
            'db:database:url': 'sqlite3://example.com',
        }

    @fixture
    def dbsettings(self, settings):
        return DatabaseSetting(settings)

    def test_get_key(self, dbsettings):
        """
        .get_key should create proper key for settings.
        """
        assert dbsettings.get_key() == 'db:database'

    def test_get_key_with_subkey(self, settings, dbsettings):
        """
        .get_key should create proper key for settings.
        """
        assert dbsettings.get_key('url') == 'db:database:url'

    def test_settings_as_dict(self, settings, dbsettings):
        """
        DatabaseSetting should act like normal dict
        """
        assert dbsettings['url'] == 'sqlite3://example.com'

    def test_settings_as_dict_set(self, settings, dbsettings):
        """
        DatabaseSetting should act like normal dict when making set.
        """
        dbsettings['newkey'] = 'newkey hey'
        assert settings['db:database:newkey'] == 'newkey hey'

    def test_get(self, dbsettings):
        """
        .get should be able to get defaults
        """
        assert dbsettings.get('emptykey', 'default') == 'default'

    def test_validate_on_error(self, dbsettings):
        """
        .validate should raise error when needed key is missing
        """
        with raises(SettingMissing):
            dbsettings.validate()

    def test_validate(self, dbsettings):
        """
        .validate should do nothing when all needed are present
        """
        dbsettings['default_url'] = dbsettings['url']

        assert dbsettings.validate() is None
