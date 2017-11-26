from mock import MagicMock
from mock import patch
from pytest import fixture

from qapla.database.application import DatabaseApplication


class TestDatabaseApplication(object):

    @fixture
    def app(self):
        return DatabaseApplication()

    @fixture
    def mdatabase_plugin(self):
        with patch('qapla.database.application.DatabasePlugin') as mock:
            yield mock

    def test_add_database_app(self, app, mdatabase_plugin):
        """
        .add_database_app should add database config to the application and
        add all the provided databases.
        """
        database = MagicMock()
        app.add_database_app([database])

        mdatabase_plugin.assert_called_once_with(app)
        mdatabase_plugin.return_value.add_to_app.assert_called_once_with()
        assert app.dbs == mdatabase_plugin.return_value
        mdatabase_plugin.return_value.add_database.assert_called_once_with(
            database)

    def test_add_database_web(self, app):
        """
        .add_database_web should add database config to the pyramid application.
        """
        app.dbs = MagicMock()
        app.add_database_web()

        app.dbs.add_to_web.assert_called_once_with()
