from sqlalchemy.orm import Session

from qq.application import Application
from qq.initializers import ApplicationInitializer
from qq.injector import SimpleInjector
from qq.plugins.settings import TESTS_KEY
from qq.plugins.settings import SettingsInjector
from qq.plugins.types import Settings


class TransactionContextManager:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc, exc_tb):
        if exc_type:
            self.session.rollback()
        elif self.settings.get(TESTS_KEY, False):
            self.session.flush()
        else:
            self.session.commit()


class TransactionDecorator:
    def __init__(
        self,
        application: Application,
        key: str,
    ):
        super().__init__()
        self.key = key
        self.app_wrapper = ApplicationInitializer(application)

    def __call__(self, method):
        def wrapper(
            *args,
            session: Session = SimpleInjector(self.key),
            settings: Settings = SettingsInjector(self.key),
            **kwargs,
        ):
            with TransactionContextManager(session, settings):
                return self.app_wrapper(method)(*args, **kwargs)

        return self.app_wrapper(wrapper)
