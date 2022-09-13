from sqlalchemy.orm import Session

from qq.application import Application
from qq.injector import InjectApplication
from qq.injector import SimpleInjector
from qq.plugins.settings import TESTS_KEY
from qq.plugins.settings import SettingsInjector
from qq.plugins.types import Settings


class TransactionRunner:
    def __init__(
        self,
        application: Application,
        key: str,
    ):
        super().__init__()
        self.key = key
        self.runner = InjectApplication(application, False)

    def __call__(self, method):
        def wrapper(
            session: Session = SimpleInjector(self.key),
            settings: Settings = SettingsInjector(self.key),
            *args,
            **kwargs,
        ):
            try:
                result = self.runner(method)(*args, **kwargs)
                if settings.get(TESTS_KEY, False):
                    settings.flush()
                else:
                    settings.commit()
                return result
            except Exception:
                session.rollback()

        return self.runner(wrapper)
