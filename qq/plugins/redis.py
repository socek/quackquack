from redis import Redis

from qq.context import Context
from qq.plugins.settings import SettingsBasedPlugin

SETTINGS_HOST_KEY = "host"
SETTINGS_PORT_KEY = "port"
SETTINGS_DB_KEY = "db"


class RedisPlugin(SettingsBasedPlugin):
    def enter(self, context: Context):
        settings = self.get_my_settings(context)
        params = dict(
            host=settings[SETTINGS_HOST_KEY],
            port=settings[SETTINGS_PORT_KEY],
            db=settings[SETTINGS_DB_KEY],
        )
        return Redis(**params)
