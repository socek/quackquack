from qq.context import Context
from qq.injector import Injector
from qq.plugins.sqlalchemy.consts import SESSIONMAKER_KEY


@Injector
def Query(context: Context, key: str):
    return context[key][SESSIONMAKER_KEY]()


@Injector
def Command(context: Context, key: str):
    session = context[key][SESSIONMAKER_KEY]()
    yield session
    session.commit()
