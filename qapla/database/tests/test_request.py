from mock import MagicMock
from mock import patch
from mock import sentinel
from pytest import fixture

from qapla.database.request import RequestDBSession
from qapla.database.request import RequestDBSessionGenerator


class FixturesMixing(object):
    registry_key = sentinel.registry_key

    @fixture
    def mrequest(self):
        return MagicMock()


class TestRequestDBSessionGenerator(FixturesMixing):

    @fixture
    def generator(self):
        return RequestDBSessionGenerator(self.registry_key)

    @fixture
    def mrequest_db(self):
        with patch('qapla.database.request.RequestDBSession') as mock:
            yield mock

    def test_call(self, generator, mrequest, mrequest_db):
        """
        RequestDBSessionGenerator should create RequestDBSession and use it
        in generation of db session for request.
        """
        assert generator(mrequest) == mrequest_db.return_value.run.return_value

        mrequest_db.assert_called_once_with(mrequest, self.registry_key)
        mrequest.add_finished_callback.assert_called_once_with(
            mrequest_db.return_value.cleanup)
        mrequest_db.return_value.run.assert_called_once_with()


class TestRequestDBSession(FixturesMixing):

    @fixture
    def request_session(self, mrequest):
        return RequestDBSession(mrequest, self.registry_key)

    @fixture
    def msession(self, request_session):
        request_session.session = MagicMock()
        return request_session.session

    @fixture
    def mmaker(self, request_session, mrequest):
        request_session.maker = MagicMock()
        mrequest.registry = {
            self.registry_key: request_session.maker,
        }
        return request_session.maker

    def test_cleanup_on_exception(self, request_session, msession, mrequest, mmaker):
        """
        .cleanup should rollback database changes on exception
        """
        mrequest.exception = True

        request_session.cleanup(mrequest)

        msession.rollback.assert_called_once_with()
        mmaker.remove.assert_called_once_with()

    def test_cleanup_on_success(self, request_session, msession, mrequest, mmaker):
        """
        .cleanup should commit changes on response success
        """
        mrequest.exception = None

        request_session.cleanup(mrequest)
        assert not msession.rollback.called
        mmaker.remove.assert_called_once_with()

    def test_run(self, request_session, mmaker):
        """
        .run should get session maker and create session from it.
        """
        del request_session.maker

        assert request_session.run() == mmaker.return_value

        assert request_session.maker == mmaker
        assert request_session.session == mmaker.return_value
