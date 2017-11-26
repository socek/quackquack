from mock import MagicMock
from mock import patch
from pytest import fixture

from qapla.database.env import AlembicEnv


class TestAlembicEnv(object):

    @fixture
    def mapp(self):
        return MagicMock()

    @fixture
    def mbase_model(self):
        return MagicMock()

    @fixture
    def mcontext(self):
        with patch('qapla.database.env.context') as mock:
            yield mock

    @fixture
    def alembic_env(self, mapp, mbase_model):
        return AlembicEnv(mapp, mbase_model, 'main')

    @fixture
    def mrun_migrations_offline(self, alembic_env):
        with patch.object(alembic_env, 'run_migrations_offline') as mock:
            yield mock

    @fixture
    def mrun_migrations_online(self, alembic_env):
        with patch.object(alembic_env, 'run_migrations_online') as mock:
            yield mock

    @fixture
    def mrun_migrations(self, alembic_env):
        with patch.object(alembic_env, 'run_migrations') as mock:
            yield mock

    @fixture
    def mdb(self, alembic_env):
        db = MagicMock()
        alembic_env.db = db
        return db

    def test_run_when_offline_mode(
        self,
        mapp,
        mcontext,
        mrun_migrations_offline,
        mrun_migrations_online,
        alembic_env,
    ):
        """
        .run should start migration offline when context returns offline mode
        """
        mcontext.is_offline_mode.return_value = True
        mcontext.config.get_main_option.return_value = False

        alembic_env.run()

        mapp.run_command.assert_called_once_with()
        mcontext.is_offline_mode.assert_called_once_with()
        mrun_migrations_offline.assert_called_once_with()
        assert not mrun_migrations_online.called

    def test_run_when_online_mode(
        self,
        mapp,
        mcontext,
        mrun_migrations_offline,
        mrun_migrations_online,
        alembic_env,
    ):
        """
        .run should start migration online when context returns online mode
        """
        mcontext.is_offline_mode.return_value = False
        mcontext.config.get_main_option.return_value = False

        alembic_env.run()

        mapp.run_command.assert_called_once_with()
        mcontext.is_offline_mode.assert_called_once_with()
        mrun_migrations_online.assert_called_once_with()
        assert not mrun_migrations_offline.called

    def test_run_migrations_offline(
        self,
        mapp,
        mcontext,
        mrun_migrations,
        alembic_env,
        mdb,
    ):
        """
        .run_migrations_offline should get url from app, configure the alembic
        context
        """
        alembic_env.run_migrations_offline()

        mdb.get_url.assert_called_once_with()
        mcontext.configure.assert_called_once_with(
            url=mdb.get_url.return_value,
            target_metadata=alembic_env.metadata,
            literal_binds=True)
        mrun_migrations.assert_called_once_with()

    def test_run_migrations_online(
        self,
        mapp,
        mcontext,
        mrun_migrations,
        alembic_env,
        mdb,
    ):
        """
        .run_migrations_online should get engine from app, configure the alembic
        context and run migrations.
        """
        connectable = alembic_env.db.get_engine.return_value

        alembic_env.run_migrations_online()

        mdb.get_engine.assert_called_once_with()
        connectable.connect.assert_called_once_with()
        mcontext.configure.assert_called_once_with(
            connection=connectable.connect.return_value.__enter__.return_value,
            target_metadata=alembic_env.metadata)
        mrun_migrations.assert_called_once_with()

    def test_run_migrations(
        self,
        mcontext,
        alembic_env,
    ):
        """
        .run_migrations should run alembic migrations.
        """
        alembic_env.run_migrations()

        mcontext.begin_transaction.assert_called_once_with()
        mcontext.run_migrations.assert_called_once_with()

    def test_init_app_when_is_test(self, mcontext, mapp, alembic_env):
        """
        ._init_app should Applicaion.run_tests if is_test is in the alembic
        config.
        """
        mcontext.config.get_main_option.return_value = False

        alembic_env._init_app()

        mapp.run_command.assert_called_once_with()
        mcontext.config.get_main_option.assert_called_once_with(
            'is_test',
            False)

    def test_init_app_when_is_not_test(self, mcontext, mapp, alembic_env):
        """
        ._init_app should Applicaion.run_command if is_test is not in the
        alembic config.
        """
        mcontext.config.get_main_option.return_value = True

        alembic_env._init_app()

        mapp.run_tests.assert_called_once_with()
        mcontext.config.get_main_option.assert_called_once_with(
            'is_test',
            False)
