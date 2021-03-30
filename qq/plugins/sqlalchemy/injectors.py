from qq.context import Context
from qq.injector import ContextManagerInjector
from qq.injector import Injector
from qq.plugins.sqlalchemy.consts import SESSIONMAKER_KEY


@Injector
def SAQuery(context: Context, key: str):
    return context[key][SESSIONMAKER_KEY]


class SACommand(ContextManagerInjector):
    def __enter__(self, context, key):
        return context[key][SESSIONMAKER_KEY]

    def __exit__(self, exc_type, exc_value, traceback, context, key):
        session = context[key][SESSIONMAKER_KEY]
        if not exc_type:
            session.commit()
