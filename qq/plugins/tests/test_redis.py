from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture

from qq.plugins.redis import SETTINGS_DB_KEY
from qq.plugins.redis import SETTINGS_HOST_KEY
from qq.plugins.redis import SETTINGS_PORT_KEY
from qq.plugins.redis import RedisPlugin

PREFIX = "qq.plugins.redis"


class TestRedisPlugin:
    @fixture
    def plugin(self):
        plugin = RedisPlugin()
        plugin.init("redis")
        return plugin

    @fixture
    def context(self):
        return MagicMock()

    @fixture
    def mget_my_settings(self, mocker, plugin):
        mock = mocker.patch.object(plugin, "get_my_settings")
        mock.return_value = {
            SETTINGS_HOST_KEY: sentinel.host,
            SETTINGS_PORT_KEY: sentinel.port,
            SETTINGS_DB_KEY: sentinel.dbkey,
        }
        return mock

    @fixture
    def mredis(self, mocker):
        return mocker.patch(f"{PREFIX}.Redis")

    def test_connection(self, plugin, mredis, context, mget_my_settings):
        """
        Plugin should start redis connection when creating context.
        """
        assert plugin.enter(context) == mredis.return_value

        mredis.assert_called_once_with(
            host=sentinel.host, port=sentinel.port, db=sentinel.dbkey
        )
