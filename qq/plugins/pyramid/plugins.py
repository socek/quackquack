from qq.plugin import Plugin
from qq.plugins.pyramid.application import PyramidApplication
from qq.plugins.settings import SettingsBasedPlugin


class BasePyramidPlugin(SettingsBasedPlugin):
    def start(self, application: PyramidApplication):
        self.settings = self.get_my_settings(application)


class AuthPlugin(BasePyramidPlugin):
    """
    Add authorization to the pyramid app.
    """

    def __init__(self, authn_policy_cls, authz_policy_cls, root_factory=None):
        self.authn_policy_cls = authn_policy_cls
        self.authz_policy_cls = authz_policy_cls
        self.root_factory = root_factory

    def start_pyramid(self, pyramid):
        authn_policy = self.authn_policy_cls(self.settings["secret"])
        authz_policy = self.authz_policy_cls()
        pyramid.set_authentication_policy(authn_policy)
        pyramid.set_authorization_policy(authz_policy)
        if self.root_factory:
            pyramid.set_root_factory(self.root_factory)


class CsrfPlugin(BasePyramidPlugin):
    """
    Add csrf mechanism to the pyramid app.
    """

    def __init__(self, policy_cls):
        self.policy_cls = policy_cls

    def start_pyramid(self, pyramid):
        pyramid.set_csrf_storage_policy(self.policy_cls())
        pyramid.set_default_csrf_options(
            require_csrf=True,
            token=self.settings["csrf_token_key"],
            header=self.settings["csrf_header_key"],
        )


class RoutingPlugin(Plugin):
    """
    Add routing to the pyramid app.
    """

    def __init__(self, routing_cls):
        self.routing_cls = routing_cls

    def start_pyramid(self, pyramid):
        self.routing = self.routing_cls(pyramid)
        self.routing.make()


class SessionPlugin(BasePyramidPlugin):
    """
    Add session mechanism to the pyramid app.
    """

    def __init__(self, session_factory_cls):
        self.session_factory_cls = session_factory_cls

    def start_pyramid(self, pyramid):
        secret = self.settings["session_secret"]
        session_factory = self.session_factory_cls(secret)
        pyramid.set_session_factory(session_factory)
