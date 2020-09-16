from redis import Redis

from sapp.plugin import Plugin


class RedisPlugin(Plugin):
    SETTINGS_HOST_KEY = "host"
    SETTINGS_PORT_KEY = "port"
    SETTINGS_DB_KEY = "db"

    def __init__(self, ctx_key="redis"):
        self.ctx_key = ctx_key

    def enter(self, context):
        settings = context.settings[self.ctx_key]
        params = dict(
            host=settings[self.SETTINGS_HOST_KEY],
            port=settings[self.SETTINGS_PORT_KEY],
            db=settings[self.SETTINGS_DB_KEY],
        )
        setattr(context, self.ctx_key, Redis(**params))
