from mock import MagicMock
from mock import patch
from mock import sentinel
from pytest import fixture

from qapla.driver import ReadDriver
from qapla.driver import WriteDriver


class FixtureMixin(object):

    @fixture
    def mdatabase(self):
        return MagicMock()

    @fixture
    def mmodel(self, driver):
        with patch.object(driver, 'model') as mock:
            yield mock


class TestReadDriver(FixtureMixin):

    @fixture
    def driver(self, mdatabase):
        return ReadDriver(mdatabase)

    def test_query(self, driver, mdatabase, mmodel):
        """
        .query should return sql query object with driver's model
        """
        assert driver.query() == mdatabase.query.return_value
        mdatabase.query.assert_called_once_with(mmodel)

    def test_get_by_id(self, driver, mdatabase, mmodel):
        """
        .get_by_id should return one object searched by id.
        """
        assert driver.get_by_id(
            sentinel.object_id) == mdatabase.query.return_value.filter.return_value.one.return_value
        mdatabase.query.return_value.filter.return_value.one.assert_called_once_with()
        mdatabase.query.return_value.filter.assert_called_once_with(mmodel.id == sentinel.object_id)
        mdatabase.query.assert_called_once_with(mmodel)


class TestWriteDriver(FixtureMixin):

    @fixture
    def driver(self, mdatabase):
        return WriteDriver(mdatabase)

    def test_create(self, driver, mdatabase, mmodel):
        """
        .create should create object from driver.model with provided values. It should add object to the session and
        commit it to the database.
        """
        assert driver.create(hello='is', it='me', you='re', looking='for') == mmodel.return_value
        mmodel.assert_called_once_with()

        assert mmodel.return_value.hello == 'is'
        assert mmodel.return_value.it == 'me'
        assert mmodel.return_value.you == 're'
        assert mmodel.return_value.looking == 'for'
        mdatabase.add.assert_called_once_with(mmodel.return_value)
        mdatabase.commit.assert_called_once_with()
