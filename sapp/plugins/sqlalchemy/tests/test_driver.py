from unittest.mock import MagicMock

from pytest import fixture

from sapp.plugins.sqlalchemy.driver import Command
from sapp.plugins.sqlalchemy.driver import Query


class Fixtures(object):
    @fixture
    def mdb(self):
        return MagicMock()

    @fixture
    def model(self):
        return MagicMock()


class TestQuery(Fixtures):
    @fixture
    def query(self, mdb, model):
        query = Query(mdb)
        query.model = model
        return query

    def test_get_by_id(self, query, mdb, model):
        """
        .get_by_id should filter the database by id and get one an only one
        element.
        """
        expected_result = (
            mdb.query.return_value.filter.return_value.one.return_value)
        assert query.get_by_id('fake-id') == expected_result

        mdb.query.assert_called_once_with(model)
        mdb.query.return_value.filter.assert_called_once_with(
            model.id == 'fake-id')

    def test_list_all(self, query, mdb, model):
        """
        .list_all should return all elements from the database.
        """
        assert query.list_all() == mdb.query.return_value.all.return_value
        mdb.query.assert_called_once_with(model)
        mdb.query.return_value.all.assert_called_once_with()


class TestCommand(Fixtures):
    @fixture
    def command(self, mdb, model):
        command = Command(mdb)
        command.model = model
        return command

    def test_create(self, command, mdb, model):
        """
        .create should create the object and add it to the database session.
        """
        obj = command.create(key='value')

        assert obj == model.return_value
        assert obj.key == 'value'
        mdb.add.assert_called_once_with(obj)
        mdb.commit.assert_called_once_with()
