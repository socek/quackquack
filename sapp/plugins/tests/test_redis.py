from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

from pytest import fixture

from sapp.plugins.redis import RedisPlugin


class TestRedisPlugin:
    @fixture
    def plugin(self):
        return RedisPlugin()

    @fixture
    def configurator(self):
        mock = MagicMock()
        mock.settings = {
            "redis": {
                RedisPlugin.SETTINGS_HOST_KEY: sentinel.host,
                RedisPlugin.SETTINGS_PORT_KEY: sentinel.port,
                RedisPlugin.SETTINGS_DB_KEY: sentinel.dbkey,
            }
        }
        return mock

    @fixture
    def context(self):
        mock = MagicMock()
        mock.settings = {
            "redis": {
                RedisPlugin.SETTINGS_HOST_KEY: sentinel.host,
                RedisPlugin.SETTINGS_PORT_KEY: sentinel.port,
                RedisPlugin.SETTINGS_DB_KEY: sentinel.dbkey,
            }
        }
        return mock

    @fixture
    def mredis(self):
        with patch("sapp.plugins.redis.Redis") as mock:
            yield mock

    def test_connection(self, plugin, configurator, mredis, context):
        """
        Plugin should start redis connection when creating context.
        """
        plugin.start(configurator)
        plugin.enter(context)

        assert context.redis == mredis.return_value
        mredis.assert_called_once_with(
            host=sentinel.host, port=sentinel.port, db=sentinel.dbkey
        )
