from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import fixture

from sapp.plugins.sqlalchemy.alembic import AlembicScript


class TestAlembicScript(object):
    @fixture
    def mapp(self):
        return MagicMock()

    @fixture
    def mmodel(self):
        return MagicMock()

    @fixture
    def script(self, mapp, mmodel):
        return AlembicScript(mapp, mmodel, 'dbname')

    @fixture
    def mcontext(self):
        with patch('sapp.plugins.sqlalchemy.alembic.context') as mock:
            yield mock

    @fixture
    def mdbplugin(self, mapp):
        mapp.dbplugins['dbname'] = MagicMock()
        return mapp.dbplugins['dbname']

    @fixture
    def mconnection(self, mdbplugin):
        return (mdbplugin.get_engine.return_value.connect.return_value.
                __enter__.return_value)

    def test_run_in_offline_mode(self, script, mcontext, mmodel, mdbplugin):
        """
        AlembicScript should run migrations in offline mode if needed.
        """
        mcontext.is_offline_mode.return_value = True

        script.run()

        mcontext.configure.assert_called_once_with(
            url=mdbplugin.get_url.return_value,
            target_metadata=mmodel.metadata,
            literal_binds=True)

        mcontext.begin_transaction.assert_called_once_with()
        mcontext.run_migrations.assert_called_once_with()

    def test_run_in_online_mode(
            self,
            script,
            mcontext,
            mmodel,
            mdbplugin,
            mconnection,
    ):
        """
        AlembicScript should run migrations in online mode if needed.
        """
        mcontext.is_offline_mode.return_value = False

        script.run()

        mcontext.configure.assert_called_once_with(
            connection=mconnection, target_metadata=mmodel.metadata)

        mcontext.begin_transaction.assert_called_once_with()
        mcontext.run_migrations.assert_called_once_with()
