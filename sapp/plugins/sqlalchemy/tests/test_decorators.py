from mock import MagicMock
from pytest import fixture

from qapla.database.decorators import WithDatabase


class TestWithDatabase(object):

    @fixture
    def mfun(self):
        return MagicMock()

    @fixture
    def mapp(self):
        mapp = MagicMock()
        mapp.dbs = dict(database=MagicMock())
        return mapp

    @fixture
    def mdb(self, mapp):
        return mapp.dbs['database']

    @fixture
    def decorator(self, mapp):
        return WithDatabase(mapp)

    @fixture
    def decorated(self, decorator, mfun):
        return decorator(mfun)

    def test_when_no_error(self, decorated, mfun, mdb):
        """
        WithDatabase should add database to the arguments of the function.
        """
        decorated('arg', second='arg2')

        mfun.asser_called_once_with('arg', database=mdb, second='arg2')

    def test_when_closing(self, decorated, mdb):
        """
        WithDatabase should close the database if not set otherwise.
        """
        decorated()

        mdb.close.asser_called_once_with()

    def test_when_not_closing(self, decorator, decorated, mdb):
        """
        WithDatabase should not close the database if close_after_end is set to
        False.
        """
        decorator.close_after_end = False

        decorated()

        assert not mdb.close.called
