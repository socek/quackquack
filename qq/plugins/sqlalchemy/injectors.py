from sqlalchemy.orm import Session

from qq.injectors import Inicjator
from qq.plugins.settings import TESTS_KEY
from qq.plugins.settings import SettingsPlugin
from qq.plugins.types import Settings


class SesssionInicjator(Inicjator):
    def __init__(self, key: str):
        self.key = key

    def start(self):
        self.session: Session = self.context[self.key]
        self.settings: Settings = self.context[SettingsPlugin.key]
        return self.session


class TransactionInicjator(SesssionInicjator):

    def finish(self, er=None):
        if er:
            self.session.rollback()
        elif self.settings.get(TESTS_KEY, False):
            self.session.flush()
        else:
            self.session.commit()
