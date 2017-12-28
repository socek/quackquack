from pytest import fixture
from unittest.mock import MagicMock
from unittest.mock import sentinel

from sapp.plugins.pyramid.plugins import AuthPlugin
from sapp.plugins.pyramid.plugins import CsrfPlugin
from sapp.plugins.pyramid.plugins import RoutingPlugin
from sapp.plugins.pyramid.plugins import SessionPlugin


class Fixtures(object):
    @fixture
    def mconfigurator(self):
        return MagicMock()

    @fixture
    def mpyramid(self):
        return MagicMock()


class TestAuthPlugin(Fixtures):
    @fixture
    def mauthn_policy_cls(self):
        return MagicMock()

    @fixture
    def mauthz_policy_cls(self):
        return MagicMock()

    @fixture
    def mroot_factory(self):
        return MagicMock()

    @fixture
    def plugin(self, mauthn_policy_cls, mauthz_policy_cls, mroot_factory):
        return AuthPlugin(mauthn_policy_cls, mauthz_policy_cls, mroot_factory)

    def test_start(self, plugin, mconfigurator):
        """
        .start should get the settings from configurator.
        """
        plugin.start(mconfigurator)

        assert plugin.settings == mconfigurator.settings

    def test_start_pyramid(self, plugin, mpyramid, mauthn_policy_cls,
                           mauthz_policy_cls, mroot_factory):
        """
        .start_pyramid should configure auth policy
        """
        plugin.settings = {'secret': sentinel.secret}
        plugin.start_pyramid(mpyramid)

        mauthn_policy_cls.assert_called_once_with(sentinel.secret)
        mauthz_policy_cls.assert_called_once_with()

        mpyramid.set_authentication_policy.assert_called_once_with(
            mauthn_policy_cls.return_value)
        mpyramid.set_authorization_policy.assert_called_once_with(
            mauthz_policy_cls.return_value)
        mpyramid.set_root_factory.assert_called_once_with(mroot_factory)

    def test_start_pyramid_without_root_factory(
            self, plugin, mpyramid, mauthn_policy_cls, mauthz_policy_cls,
            mroot_factory):
        """
        .start_pyramid without root_factory should configure auth policy without
        root_factory
        """
        plugin.settings = {'secret': sentinel.secret}
        plugin.root_factory = None
        plugin.start_pyramid(mpyramid)

        mauthn_policy_cls.assert_called_once_with(sentinel.secret)
        mauthz_policy_cls.assert_called_once_with()

        mpyramid.set_authentication_policy.assert_called_once_with(
            mauthn_policy_cls.return_value)
        mpyramid.set_authorization_policy.assert_called_once_with(
            mauthz_policy_cls.return_value)
        assert not mpyramid.set_root_factory.called


class TestCsrfPlugin(Fixtures):
    @fixture
    def mpolicy_cls(self):
        return MagicMock()

    @fixture
    def plugin(self, mpolicy_cls):
        return CsrfPlugin(mpolicy_cls)

    def test_start(self, plugin, mconfigurator):
        """
        .start should get the settings from configurator.
        """
        plugin.start(mconfigurator)

        assert plugin.settings == mconfigurator.settings

    def test_start_pyramid(self, plugin, mpyramid, mpolicy_cls):
        """
        .start_pyramid should configure csrf
        """
        plugin.settings = {
            'csrf_token_key': sentinel.csrf_token_key,
            'csrf_header_key': sentinel.csrf_header_key
        }

        plugin.start_pyramid(mpyramid)

        mpolicy_cls.assert_called_once_with()
        mpyramid.set_csrf_storage_policy(mpolicy_cls.return_value)
        mpyramid.set_default_csrf_options.assert_called_once_with(
            require_csrf=True,
            token=sentinel.csrf_token_key,
            header=sentinel.csrf_header_key)


class TestRoutingPlugin(Fixtures):
    @fixture
    def mrouting_cls(self):
        return MagicMock()

    @fixture
    def plugin(self, mrouting_cls):
        return RoutingPlugin(mrouting_cls)

    def test_start_pyramid(self, plugin, mpyramid, mrouting_cls):
        """
        .start_pyramid should start routing.
        """
        plugin.start_pyramid(mpyramid)
        mrouting_cls.assert_called_once_with(mpyramid)
        mrouting_cls.return_value.make.assert_called_once_with()


class TestSessionPlugin(Fixtures):
    @fixture
    def msession_factory_cls(self):
        return MagicMock()

    @fixture
    def plugin(self, msession_factory_cls):
        return SessionPlugin(msession_factory_cls)

    def test_start(self, plugin, mconfigurator):
        """
        .start should get the settings from configurator.
        """
        plugin.start(mconfigurator)

        assert plugin.settings == mconfigurator.settings

    def test_start_pyramid(self, plugin, mpyramid, msession_factory_cls):
        """
        .start_pyramid should configure csrf
        """
        plugin.settings = {
            'session_secret': sentinel.session_secret,
        }

        plugin.start_pyramid(mpyramid)

        msession_factory_cls.assert_called_once_with(sentinel.session_secret)
        mpyramid.set_session_factory.assert_called_once_with(
            msession_factory_cls.return_value)
