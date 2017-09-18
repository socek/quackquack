from mock import MagicMock
from pytest import fixture
from pytest import raises

from qapla.database.request import RequestDBSessionGenerator


class TestRequestDBSessionGenerator(object):

    @fixture
    def generator(self):
        return RequestDBSessionGenerator()

    @fixture
    def mrequest(self):
        return MagicMock()

    @fixture
    def msession(self, generator):
        generator.session = MagicMock()
        return generator.session

    def test_call(self, generator, mrequest):
        """
        .__call__ should create new session and add cleanup step for it.
        """
        assert generator(mrequest) == mrequest.registry.sessionmaker.return_value

        mrequest.registry.sessionmaker.assert_called_once_with()
        mrequest.add_finished_callback(generator.cleanup)

    def test_cleanup_on_exception(self, generator, msession, mrequest):
        """
        .cleanup should rollback database changes on exception
        """
        mrequest.exception = True

        generator.cleanup(mrequest)
        msession.rollback.assert_called_once_with()
        msession.close.assert_called_once_with()

    def test_cleanup_on_commit_exception(self, generator, msession, mrequest):
        """
        .cleanup should rollback database changes on commit's exception.
        This is not very often, but we need to rollback changes and re-raise
        the error.
        """
        mrequest.exception = None
        msession.commit.side_effect = RuntimeError('x')

        with raises(RuntimeError):
            generator.cleanup(mrequest)

        msession.rollback.assert_called_once_with()
        msession.close.assert_called_once_with()

    def test_cleanup_on_success(self, generator, msession, mrequest):
        """
        .cleanup should commit changes on response success
        """
        mrequest.exception = None

        generator.cleanup(mrequest)
        msession.commit.assert_called_once_with()
        msession.close.assert_called_once_with()
