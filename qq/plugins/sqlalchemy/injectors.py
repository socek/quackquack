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
        self, key: str
    ):
        super().__init__()
        self.key = key

    def __enter__(self, context) -> Session:
        return context[self.key]

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
        context,
    ):
        settings = context[SettingsPlugin.key][self.key]
        db = context[self.key]
        if settings.get(TESTS_KEY, False):
            db.flush()
        elif not exc_type:
            db.commit()
