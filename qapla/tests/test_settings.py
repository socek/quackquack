from mock import patch
from mock import sentinel
from pytest import fixture

from qapla.settings import SettingsFactory


class TestSettingsFactory(object):

    @fixture
    def factory(self):
        return SettingsFactory('mymodule')

    @fixture
    def mgenerate_settings(self, factory):
        with patch.object(factory, '_generate_settings') as mock:
            yield mock

    @fixture
    def mfactory(self):
        with patch('qapla.settings.Factory') as mock:
            yield mock

    def test_get_for(self, factory, mgenerate_settings):
        """
        ._get_for should generate settings for proper endpoint.
        """
        factory.get_for('uwsgi')

        mgenerate_settings.assert_called_once_with(factory.ENDPOINTS['uwsgi'])

    def test_generate_settings(self, factory, mfactory):
        """
        ._generate_settings should create factory from provided files and return settings and paths
        """
        mfactory.return_value.make_settings.return_value = (sentinel.left, sentinel.right)

        assert factory._generate_settings(['one', 'two', 'three']) == (sentinel.left, sentinel.right)

        mfactory.assert_called_once_with('mymodule')
        mfactory.return_value.make_settings.assert_called_once_with(
            settings=factory.settings,
            additional_modules=['one', 'two', 'three'])
