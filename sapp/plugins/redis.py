from redis import Redis

from sapp.context import Context
from sapp.plugins.settings import SettingsBasedPlugin

SETTINGS_HOST_KEY = "host"
SETTINGS_PORT_KEY = "port"
SETTINGS_DB_KEY = "db"


class RedisPlugin(SettingsBasedPlugin):
    DEFAULT_KEY = "redis"

    def enter(self, context: Context):
        settings = self.get_my_settings(context=context)
        params = dict(
            host=settings[SETTINGS_HOST_KEY],
            port=settings[SETTINGS_PORT_KEY],
            db=settings[SETTINGS_DB_KEY],
        )
        return Redis(**params)
