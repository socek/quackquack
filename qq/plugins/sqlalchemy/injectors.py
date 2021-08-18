from sqlalchemy.orm import Session

from qq.context import Context
from qq.injector import ContextManagerInjector
from qq.injector import Injector
from qq.plugins.settings import TESTS_KEY
from qq.plugins.settings import SettingsPlugin


@Injector
def SAQuery(context: Context, key: str) -> Session:
    return context[key]


class SACommand(ContextManagerInjector):
    def __init__(
        self, key: str, settings_key: str = SettingsPlugin.DEFAULT_KEY
    ):
        super().__init__()
        self.key = key
        self.settings_key = settings_key

    def __enter__(self, context) -> Session:
        return context[self.key]

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
        context,
    ):
        settings = context[self.settings_key][self.key]
        db = context[self.key]
        if settings.get(TESTS_KEY, False):
            db.flush()
        elif not exc_type:
            db.commit()
