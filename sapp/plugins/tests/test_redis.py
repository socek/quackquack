from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

from pytest import fixture

from sapp.plugins.redis import RedisPlugin


class TestRedisPlugin(object):
    @fixture
    def plugin(self):
        return RedisPlugin()

    @fixture
    def configurator(self):
        mock = MagicMock()
        mock.settings = {
            RedisPlugin.SETTINGS_HOST_KEY: sentinel.host,
            RedisPlugin.SETTINGS_PORT_KEY: sentinel.port,
            RedisPlugin.SETTINGS_DB_KEY: sentinel.dbkey,
        }
        return mock

    @fixture
    def mstrict_redis(self):
        with patch("sapp.plugins.redis.StrictRedis") as mock:
            yield mock

    def test_connection(self, plugin, configurator, mstrict_redis):
        """
        Plugin should start redis connection when creating context.
        """
        plugin.start(configurator)
        context = MagicMock()

        plugin.enter(context)

        assert context.redis == mstrict_redis.return_value
        mstrict_redis.assert_called_once_with(
            host=sentinel.host, port=sentinel.port, db=sentinel.dbkey
        )
