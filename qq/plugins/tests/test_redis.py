from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

from pytest import fixture

from qq.plugins.redis import SETTINGS_DB_KEY
from qq.plugins.redis import SETTINGS_HOST_KEY
from qq.plugins.redis import SETTINGS_PORT_KEY
from qq.plugins.redis import RedisPlugin


class TestRedisPlugin:
    @fixture
    def plugin(self):
        plugin = RedisPlugin()
        plugin._set_key("redis")
        return plugin

    @fixture
    def configurator(self):
        mock = MagicMock()
        mock.extra = {
            "settings": {
                "redis": {
                    SETTINGS_HOST_KEY: sentinel.host,
                    SETTINGS_PORT_KEY: sentinel.port,
                    SETTINGS_DB_KEY: sentinel.dbkey,
                }
            }
        }
        return mock

    @fixture
    def context(self):
        return {
            "settings": {
                "redis": {
                    SETTINGS_HOST_KEY: sentinel.host,
                    SETTINGS_PORT_KEY: sentinel.port,
                    SETTINGS_DB_KEY: sentinel.dbkey,
                }
            }
        }

    @fixture
    def mredis(self):
        with patch("qq.plugins.redis.Redis") as mock:
            yield mock

    def test_connection(self, plugin, configurator, mredis, context):
        """
        Plugin should start redis connection when creating context.
        """
        plugin.start(configurator)
        assert plugin.enter(context) == mredis.return_value

        mredis.assert_called_once_with(
            host=sentinel.host, port=sentinel.port, db=sentinel.dbkey
        )
