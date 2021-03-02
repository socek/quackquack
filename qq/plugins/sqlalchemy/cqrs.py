from unittest.mock import patch

from qq.decorators import Decorator
from qq.plugins.sqlalchemy.consts import DATABASES_KEY


class SqlQuery:
    def __init__(self, application, name):
        self.application = application
        self.name = name

    def __call__(self, fun):
        return Decorator(self.application, self.name)(fun)


class SqlCommand:
    class CommitContext:
        def __init__(self, name, kwargs):
            self.session = kwargs[name]
            self._commit = kwargs.pop("commit", True)

        def __enter__(self):
            pass

        def __exit__(self, type: type, value: Exception, traceback):
            if value:
                self.session.rollback()
            elif self._commit:
                self.session.commit()

    class MockCommitContext(CommitContext):
        def __enter__(self):
            self._patcher = patch.object(self.session, "commit")
            self.mcommit = self._patcher.start()
            self.mcommit.side_effect = self.session.flush

        def __exit__(self, type: type, value: Exception, traceback):
            self._patcher.stop()
            if value:
                self.session.rollback()
            elif self._commit:
                self.session.flush()

    def __init__(self, application, name):
        self.application = application
        self.name = name

    def __call__(self, fun):
        @Decorator(self.application, "settings")
        def wrapper(*args, settings=None, **kwargs):
            is_tests = settings[DATABASES_KEY][self.name].get("tests", False)
            ctx = self.MockCommitContext if is_tests else self.CommitContext
            with ctx(self.name, kwargs):
                return fun(*args, **kwargs)

        return Decorator(self.application, self.name)(wrapper)
