from redis import StrictRedis

from sapp.plugin import Plugin


class RedisPlugin(Plugin):
    SETTINGS_HOST_KEY = "redis:host"
    SETTINGS_PORT_KEY = "redis:port"
    SETTINGS_DB_KEY = "redis:db"

    def start(self, configurator):
        self.settings = configurator.settings

    def enter(self, context):
        params = dict(
            host=self.settings[self.SETTINGS_HOST_KEY],
            port=self.settings[self.SETTINGS_PORT_KEY],
            db=self.settings[self.SETTINGS_DB_KEY],
        )
        setattr(context, "redis", StrictRedis(**params))
